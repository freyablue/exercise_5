/* For room.html */

// TODO: Fetch the list of existing chat messages.
// POST to the API when the user posts a new message.
// Automatically poll for new messages on a regular interval.
// Allow changing the name of a room
function postMessage() {
  fetch('/api/room/<room_id>/messages', {
    method: 'POST',
    header: {
      'Content-Type': 'application/json',
      'API-Key':'your_api_key',
    },
    body: JSON.stringify({content: content}),
  })
  .then(response => response.json())
  .then(result =>{
    console.log("Message Posted: ", result);
  })
  .catch(error=> console.error('Error Posting Message ', error));
}

function getMessages() {
  fetch('/api/room/<room_id>/messages', {
    method: 'GET',
    headers: {
        'API-Key': 'your_api_key',
    },
  })
  .then(response => response.json())
  .then(messages => {
    // Process and display messages
    console.log('Fetched Messages:', messages);
  })
  .catch(error => console.error('Error Fetching Messages:', error));
}

function startMessagePolling() {
  setInterval(function () {
    getMessages();
  }, 100);  // the interval
}

function updateRoomName(newRoomName) {
  fetch('/api/room/update-name', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
        'API-Key': 'your_api_key',
    },
    body: JSON.stringify({ new_room_name: newRoomName }),
  })
  .then(response => response.json())
  .then(result => {
    // Handle success
    console.log('Success:', result);
  })
  .catch(error => console.error('Error Updating Name:', error));
}

/* For profile.html */

// TODO: Allow updating the username and password

function updateUsername(newUsername) {
  fetch('/api/user/username', {
      method: 'PUT',
      headers: {
          'Content-Type': 'application/json',
          'API-Key': 'your_api_key',
      },
      body: JSON.stringify({ new_username: newUsername }),
  })
  .then(response => response.json())
  .then(result => {
      // Handle success
      console.log('Username updated successfully:', result);
  })
  .catch(error => console.error('Error updating username:', error));
}

function updatePassword(newPassword) {
  fetch('/api/user/password', {
      method: 'PUT',
      headers: {
          'Content-Type': 'application/json',
          'API-Key': 'your_api_key',
      },
      body: JSON.stringify({ new_password: newPassword }),
  })
  .then(response => response.json())
  .then(result => {
      // Handle success
      console.log('Password updated successfully:', result);
  })
  .catch(error => console.error('Error updating password:', error));
}