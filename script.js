let websocket;
let conversationId;

async function fetchMessages(conversation_id) {
    const response = await fetch(`http://localhost:8000/messages/${conversation_id}`);
    const messages = await response.json();
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = ''; // Clear existing messages
    messages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.innerHTML = `<span class="username">${message.ehempid}:</span> <span class="content">${message.content}</span>`;
        chatbox.appendChild(messageElement);
    });
}

async function connect() {
    const username = document.getElementById('username').value;
    const ehempid1 = document.getElementById('ehempid1').value;
    const ehempid2 = document.getElementById('ehempid2').value;
    if (!username || !ehempid1 || !ehempid2) {
        alert("Please enter all required fields");
        return;
    }
    if (websocket) {
        alert("Already connected");
        return;
    }
    websocket = new WebSocket(`ws://localhost:8000/ws/chat/${ehempid1}/${ehempid2}/${username}`);

    websocket.onmessage = function(event) {
        const chatbox = document.getElementById('chatbox');
        const message = document.createElement('div');
        message.classList.add('chat-message');
        message.innerHTML = `<span class="username">${username}:</span> <span class="content">${event.data}</span>`;
        chatbox.appendChild(message);
    };

    websocket.onclose = function(event) {
        const chatbox = document.getElementById('chatbox');
        const message = document.createElement('div');
        message.classList.add('chat-message');
        message.innerHTML = `<span class="content">Disconnected from chat</span>`;
        chatbox.appendChild(message);
        websocket = null;
    };

    // Fetch and display existing messages when connecting
    const response = await fetch(`http://localhost:8000/conversations?ehempid1=${ehempid1}&ehempid2=${ehempid2}`);
    const data = await response.json();
    conversationId = data.conversation_id;
    fetchMessages(conversationId);
}

function sendMessage() {
    const message = document.getElementById('message').value;
    if (!websocket) {
        alert("You are not connected to the chat");
        return;
    }
    websocket.send(message);
    document.getElementById('message').value = '';
}

function disconnect() {
    if (websocket) {
        websocket.close();
        websocket = null;
    } else {
        alert("You are not connected to the chat");
    }
}