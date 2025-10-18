// Add this JavaScript to your main UI to fix the "AI is typing" issue

// Handle AI typing events
socket.on('ai_typing', (data) => {
    console.log('AI typing event:', data);
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        if (data.typing) {
            typingIndicator.style.display = 'block';
            typingIndicator.textContent = 'AI is typing...';
        } else {
            typingIndicator.style.display = 'none';
        }
    }
});

// Enhanced new_message handler
socket.on('new_message', (data) => {
    console.log('New message received:', data);
    
    // Hide typing indicator when message arrives
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
    
    // Add the message to chat
    const role = data.role === 'ai' ? 'AI Assistant' : 
                 data.role === 'agent' ? 'Human Agent' : 'You';
    
    // Your existing message handling code here
    addMessage(data.role, `${role}: ${data.content}`);
});

// Add this CSS to your main UI
const typingCSS = `
<style>
#typing-indicator {
    display: none;
    padding: 10px;
    margin: 10px 0;
    background: #f0f0f0;
    border-radius: 5px;
    font-style: italic;
    color: #666;
    text-align: center;
}
</style>
`;

// Add the CSS to the page
document.head.insertAdjacentHTML('beforeend', typingCSS);

// Add typing indicator to your chat container
const chatContainer = document.querySelector('.chat-messages, .chat-container, #chat');
if (chatContainer) {
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.textContent = 'AI is typing...';
    chatContainer.appendChild(typingDiv);
}
