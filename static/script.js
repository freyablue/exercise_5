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

function updateRoomName(newName) {
  fetch('/api/room/update-name', {
    
  })
}

/* For profile.html */

// TODO: Allow updating the username and password
