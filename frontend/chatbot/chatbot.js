import { BACKEND_URL } from "./../shared.js"

const themeToggle = document.querySelector('.theme-toggle');
const body = document.body;
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.querySelector('.message-input');
const sendButton = document.querySelector('.send-button');
const typingIndicator = document.querySelector('.typing-indicator');

// Theme toggling
let isDarkTheme = false;
themeToggle.addEventListener('click', () => {
    isDarkTheme = !isDarkTheme;
    body.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
    themeToggle.innerHTML = isDarkTheme ? 
        '<i class="fas fa-sun"></i>' : 
        '<i class="fas fa-moon"></i>';
});

// Chat functionality
function createMessageElement(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    let userName = localStorage.getItem("email").split("@")[0][0].toUpperCase()
    messageDiv.innerHTML = `
        <div class="avatar">${isUser ? userName : 'AI'}</div>
        <div class="message-bubble">${content}</div>
    `;
    
    return messageDiv;
}

function addMessage(content, isUser = false) {
    const messageElement = createMessageElement(content, isUser);
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

async function simulateBotResponse(userMessage) {
    showTypingIndicator();
    let response =  await askQuestion(localStorage.getItem("email"),userMessage);
    hideTypingIndicator();
    addMessage(response);
}

function handleSendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        addMessage(message, true);
        messageInput.value = '';
        simulateBotResponse(message);
    }
}

sendButton.addEventListener('click', handleSendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

setTimeout(() => {
    addMessage("Hello! I'm your AI assistant. How can I help you today?");
}, 500);


async function askQuestion(email, userQuestion) {
    try {
      const response = await fetch(`${BACKEND_URL}askbackend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email,
          user_question: userQuestion
        })
      });
  
      if (!response.ok) {
        // throw new Error(`HTTP error! Status: ${response.status}`);
        return "There was some issue fetching data";
      }
  
      const data = await response.json();
      return data["response"];  // You can return the result to be used elsewhere
    } catch (error) {
        console.error("API call failed:", error);
    //   throw error;  // Optional: rethrow for higher-level error handling
        return "There was some issue fetching data";

    }
  }