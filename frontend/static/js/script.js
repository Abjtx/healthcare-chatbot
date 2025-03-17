document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    
    // Generate a unique user ID for this session
    const userId = 'user_' + Math.random().toString(36).substring(2, 15);
    
    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Handle different message types
        if (typeof message === 'string') {
            // Text message
            const paragraph = document.createElement('p');
            
            // Convert URLs to clickable links
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            const textWithLinks = message.replace(urlRegex, function(url) {
                return `<a href="${url}" target="_blank">${url}</a>`;
            });
            
            // Convert newlines to <br> tags
            const textWithBreaks = textWithLinks.replace(/\n/g, '<br>');
            
            paragraph.innerHTML = textWithBreaks;
            messageContent.appendChild(paragraph);
        } else if (message.image) {
            // Image message
            const img = document.createElement('img');
            img.src = message.image;
            img.alt = 'Bot shared an image';
            img.style.maxWidth = '100%';
            messageContent.appendChild(img);
        } else if (message.custom) {
            // Custom message (like buttons, etc.)
            messageContent.innerHTML = message.custom;
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator-container';
        typingDiv.id = 'typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'message-content typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingContent.appendChild(dot);
        }
        
        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Function to send message to the backend
    async function sendMessage(message) {
        try {
            showTypingIndicator();
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    user_id: userId
                })
            });
            
            hideTypingIndicator();
            
            if (!response.ok) {
                throw new Error('Failed to get response from server');
            }
            
            const data = await response.json();
            
            if (data.error) {
                addMessage('Sorry, I encountered an error: ' + data.error);
                return;
            }
            
            // Display bot responses
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    if (msg.text) {
                        addMessage(msg.text);
                    } else if (msg.image) {
                        addMessage({ image: msg.image });
                    } else if (msg.custom) {
                        addMessage({ custom: msg.custom });
                    }
                });
            } else {
                addMessage("I'm not sure how to respond to that.");
            }
            
        } catch (error) {
            hideTypingIndicator();
            console.error('Error:', error);
            addMessage('Sorry, there was an error communicating with the server. Please try again later.');
        }
    }
    
    // Handle send button click
    sendButton.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';
            sendMessage(message);
        }
    });
    
    // Handle Enter key press
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                addMessage(message, true);
                userInput.value = '';
                sendMessage(message);
            }
        }
    });
    
    // Focus on input field when page loads
    userInput.focus();
}); 