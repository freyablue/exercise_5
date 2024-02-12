import logging
import string
import traceback
import random
import sqlite3
from datetime import datetime
from flask import * # Flask, g, redirect, render_template, request, url_for
from functools import wraps

app = Flask(__name__)

# These should make it so your Flask app always returns the latest version of
# your HTML, CSS, and JS files. We would remove them from a production deploy,
# but don't change them here.
app.debug = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache"
    return response



def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect('db/watchparty.sqlite3')
        db.row_factory = sqlite3.Row
        setattr(g, '_database', db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cursor = db.execute(query, args)
    print("query_db")
    print(cursor)
    rows = cursor.fetchall()
    print(rows)
    db.commit()
    cursor.close()
    if rows:
        if one: 
            return rows[0]
        return rows
    return None

def new_user():
    name = "Unnamed User #" + ''.join(random.choices(string.digits, k=6))
    password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    api_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))
    u = query_db('insert into users (name, password, api_key) ' + 
        'values (?, ?, ?) returning id, name, password, api_key',
        (name, password, api_key),
        one=True)
    return u

def get_user_from_cookie(request):
    user_id = request.cookies.get('user_id')
    password = request.cookies.get('user_password')
    if user_id and password:
        return query_db('select * from users where id = ? and password = ?', [user_id, password], one=True)
    return None

def render_with_error_handling(template, **kwargs):
    try:
        return render_template(template, **kwargs)
    except:
        t = traceback.format_exc()
        return render_template('error.html', args={"trace": t}), 500

# ------------------------------ NORMAL PAGE ROUTES ----------------------------------

@app.route('/')
def index():
    print("index") # For debugging
    user = get_user_from_cookie(request)

    if user:
        rooms = query_db('select * from rooms')
        return render_with_error_handling('index.html', user=user, rooms=rooms)
    
    return render_with_error_handling('index.html', user=None, rooms=None)

@app.route('/rooms/new', methods=['GET', 'POST'])
def create_room():
    print("create room") # For debugging
    user = get_user_from_cookie(request)
    if user is None: return {}, 403

    if (request.method == 'POST'):
        name = "Unnamed Room " + ''.join(random.choices(string.digits, k=6))
        room = query_db('insert into rooms (name) values (?) returning id', [name], one=True)            
        return redirect(f'{room["id"]}')
    else:
        return app.send_static_file('create_room.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("signup")
    user = get_user_from_cookie(request)

    if user:
        return redirect('/profile')
        # return render_with_error_handling('profile.html', user=user) # redirect('/')
    
    if request.method == 'POST':
        u = new_user()
        print("u")
        print(u)
        for key in u.keys():
            print(f'{key}: {u[key]}')

        resp = redirect('/profile')
        resp.set_cookie('user_id', str(u['id']))
        resp.set_cookie('user_password', u['password'])
        return resp
    
    return redirect('/login')

@app.route('/profile')
def profile():
    print("profile")
    user = get_user_from_cookie(request)
    if user:
        return render_with_error_handling('profile.html', user=user)
    
    redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    user = get_user_from_cookie(request)

    if user:
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['name']
        u = query_db('select * from users where name = ? and password = ?', [name, password], one=True)
        if user:
            resp = make_response(redirect("/"))
            resp.set_cookie('user_id', u.id)
            resp.set_cookie('user_password', u.password)
            return resp

    return render_with_error_handling('login.html', failed=True)   

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('user_id', '')
    resp.set_cookie('user_password', '')
    return resp

@app.route('/rooms/<int:room_id>')
def room(room_id):
    user = get_user_from_cookie(request)
    if user is None: return redirect('/')

    room = query_db('select * from rooms where id = ?', [room_id], one=True)
    return render_with_error_handling('room.html',
            room=room, user=user)

# -------------------------------- API ROUTES ----------------------------------

# # GET to get all the messages in a room
# @app.route('/api/messages/<int:room_id>', methods=['GET'])
# def get_all_messages(room_id):
#     user = get_user_from_cookie(request)
#     if user is None:
#         return jsonify({'error': 'Unauthorized'}), 401

#     # TODO: Implement logic to fetch all messages in the current room
#     # Example: Fetch messages from the database
#     #room_id = user['current_room_id']
#     messages = query_db('SELECT * FROM messages WHERE room_id = ?', [room_id])
    
#     return jsonify(messages)

# # POST to post a new message to a room
# @app.route('/api/messages', methods=['POST'])
# def post_message():
#     api_key = request.headers.get('API-Key')
#     if not api_key:
#         return jsonify({'error': 'API key missing'}), 401
#     # Validate the API key 
#     if not validate_api_key(api_key):
#         return jsonify({'error': 'Invalid API key'}), 401

#     # TODO: Implement logic to post a new message to the current room
#     # Example: Insert a new message into the database
#     user_id = get_user_id_by_api_key(api_key)  
#     room_id = request.json.get('room_id')  
#     body = request.json.get('content')  
#     query_db('INSERT INTO messages (user_id, room_id, body) VALUES (?, ?, ?)',
#              [user_id, room_id, body])

#     return jsonify({'success': True})

# def validate_api_key(api_key):
#     user = query_db('SELECT * FROM users WHERE api_key = ?', [api_key], one=True)
#     return user is not None

# def get_user_id_by_api_key(api_key):
#     user = query_db('SELECT id FROM users WHERE api_key = ?', [api_key], one=True)
#     return user['id'] if user else None
# POST to change the user's name
@app.route('/api/user/name', methods=['POST'])
def update_username():
    #return {}, 403
    user = get_user_from_cookie(request)
    if user is None:
        return jsonify({'error': 'Unauthorized'}), 401

    # TODO: Implement username update logic here
    # Example: Update the user's name in the database
    new_name = request.json.get('new_username')
    query_db('UPDATE users SET name = ? WHERE id = ?', [new_name, user['id']])
    
    return jsonify({'success': True})


# POST to change the user's password
@app.route('/api/user/password', methods=['POST'])
def update_password():
    user = get_user_from_cookie(request)
    if user is None:
        return jsonify({'error': 'Unauthorized'}), 401

    # TODO: Implement password update logic here
    # Example: Update the user's password in the database
    new_password = request.json.get('new_password')
    query_db('UPDATE users SET password = ? WHERE id = ?', [new_password, user['id']])
    
    return jsonify({'success': True})
# POST to change the name of a room
@app.route('/api/room/name', methods=['POST'])
def update_room_name():
    user = get_user_from_cookie(request)
    if user is None:
        return jsonify({'error': 'Unauthorized'}), 401

    # TODO: Implement room name update logic here
    # Example: Update the room's name in the database
    room_id = user['current_room_id']
    new_name = request.json.get('new_room_name')
    query_db('UPDATE rooms SET name = ? WHERE id = ?', [new_name, room_id])
    
    return jsonify({'success': True})

# GET to get all the messages in a room
@app.route('/api/room/<int:room_id>/messages', methods=['GET'])
def get_all_messages(room_id):
    user = get_user_from_cookie(request)
    if user is None:
        return jsonify({'error': 'Unauthorized'}), 401

    # TODO: Implement logic to fetch all messages in the current room
    # Example: Fetch messages from the database
    # room_id = user['current_room_id']
    

    messages = query_db('SELECT * FROM messages WHERE room_id = ?', [room_id])
    messages_dict = [dict(row) for row in messages]
    
    return jsonify(messages_dict)
# POST to post a new message to a room
# @app.route('/api/messages', methods=['POST'])
@app.route('/api/room/<int:room_id>/messages', methods=['POST'])
def post_message(room_id):
    user = get_user_from_cookie(request)
    if user is None:
        return jsonify({'error': 'Unauthorized'}), 401

    # TODO: Implement logic to post a new message to the current room
    # Example: Insert a new message into the database
    #room_id = user['current_room_id']
    content = request.json.get('content')
    timestamp = datetime.utcnow().isoformat()
    query_db('INSERT INTO messages (user_id, room_id, body, timestamp) VALUES (?, ?, ?, ?)',
             [user['id'], room_id, content, timestamp])
    
    return jsonify({'success': True})