# Telecom Support Chatbot - User Interface

A modern React-based chat interface for an AI-powered telecom support chatbot with seamless AI-to-human agent escalation.

## Features

- 🤖 **AI Chat Interface**: Clean, modern chat UI with Material UI components
- 🔄 **Real-time Communication**: Socket.IO integration for instant messaging
- 👥 **Agent Escalation**: Smooth transition from AI to human agents
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⚡ **Typing Indicators**: Visual feedback when AI is responding
- 💾 **Session Management**: Automatic session creation and persistence
- 🎨 **Custom Styling**: Beautiful message bubbles and animations

## Tech Stack

- **React 18** - Frontend framework
- **Material UI 5** - Component library
- **Socket.IO Client** - Real-time communication
- **JavaScript** - No TypeScript (as requested)

## Project Structure

```
user-chatbot/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChatWindow.js      # Main chat interface
│   │   └── MessageBubble.js   # Individual message component
│   ├── App.js                 # Main app component
│   ├── index.js              # React entry point
│   ├── socket.js             # Socket.IO connection manager
│   └── styles.css            # Custom styles
├── package.json
└── README.md
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd user-chatbot
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

3. **Open in Browser**
   - Navigate to `http://localhost:3000`
   - The app will automatically connect to the backend at `http://localhost:5000`

## Backend Connection

The app expects a Flask backend with Socket.IO support running on `http://localhost:5000`. The backend should handle:

- **Session Management**: `join_session` events
- **Message Handling**: `user_message` events
- **AI Responses**: `ai_response` events
- **Agent Responses**: `agent_response` events
- **Escalation**: `escalation` events
- **Typing Indicators**: `typing` events

## Key Components

### ChatWindow.js
- Main chat interface with real-time messaging
- Input handling and message sending
- Connection status monitoring
- Escalation message display

### MessageBubble.js
- Individual message rendering
- Different styles for user, AI, and agent messages
- Typing indicators with animation
- Timestamp display

### socket.js
- Socket.IO connection management
- Session creation and joining
- Message sending and receiving
- Event handling for all chat features

## Features in Detail

### Message Types
- **User Messages**: Blue bubbles on the right
- **AI Messages**: Gray bubbles on the left with AI avatar
- **Agent Messages**: Gray bubbles on the left with agent avatar
- **Typing Indicators**: Animated dots when AI is responding

### Escalation Flow
1. User sends message
2. AI processes and responds
3. If escalation needed, shows "Connecting you to a specialist..."
4. Agent takes over seamlessly
5. All messages appear in the same chat interface

### Responsive Design
- Mobile-first approach
- Adaptive message bubble sizes
- Touch-friendly interface
- Optimized for various screen sizes

## Customization

### Styling
- Modify `src/styles.css` for custom styles
- Update Material UI theme in `src/App.js`
- Customize message bubble appearance in `MessageBubble.js`

### Backend URL
- Change server URL in `src/socket.js` (line 6)
- Default: `http://localhost:5000`

### Session Management
- Sessions are automatically created and stored in localStorage
- Session ID format: `session_[random]_[timestamp]`
- Sessions persist across browser refreshes

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Environment Variables
- `REACT_APP_SERVER_URL` - Backend server URL (optional)

## Production Deployment

1. Build the app: `npm run build`
2. Serve the `build` folder with a static file server
3. Ensure the backend server is accessible from the frontend domain
4. Update the server URL in `socket.js` if needed

## Troubleshooting

### Connection Issues
- Check if backend server is running on port 5000
- Verify CORS settings on the backend
- Check browser console for connection errors

### Message Display Issues
- Ensure proper message format from backend
- Check socket event names match between frontend and backend
- Verify message sender types ('user', 'ai', 'agent')

### Styling Issues
- Clear browser cache
- Check for CSS conflicts
- Verify Material UI theme is properly applied
