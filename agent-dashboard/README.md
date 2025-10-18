# Agent Dashboard

A modern, responsive dashboard for human agents in an AI-powered telecom chatbot system. Built with React and Material UI, this dashboard allows agents to manage escalated chat sessions, communicate with customers in real-time, and close sessions when complete.

## Features

### 🎯 Core Functionality
- **Real-time WebSocket Connection**: Connects to the backend chat system using Socket.IO
- **Escalation Management**: View and manage pending chat escalations
- **Live Chat Interface**: Communicate directly with customers in real-time
- **Session Management**: Join, monitor, and close chat sessions
- **AI-Generated Summaries**: View chat summaries and customer information

### 🎨 User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Material UI Components**: Modern, accessible UI components
- **Real-time Updates**: Live notifications and status updates
- **Intuitive Layout**: Left panel for chat list, right panel for active chat
- **Visual Indicators**: Connection status, message types, and priority levels

### 🔧 Technical Features
- **WebSocket Events**: Handles `escalation_pending`, `chat_message`, `session_closed`
- **State Management**: Efficient React state management for real-time updates
- **Error Handling**: Comprehensive error handling and user feedback
- **Connection Recovery**: Automatic reconnection and status monitoring

## Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/
│   ├── ChatList.js          # Left panel - list of pending escalations
│   ├── ChatWindow.js        # Right panel - active chat interface
│   └── ChatSummary.js       # AI-generated chat summary component
├── App.js                   # Main application component
├── socket.js               # WebSocket connection management
├── index.js                # Application entry point
└── index.css               # Global styles and custom CSS
```

## WebSocket Events

### Outgoing Events (Agent → Server)
- `agent_join_room` - Join a chat room
- `agent_leave_room` - Leave a chat room
- `agent_message` - Send message to customer
- `close_session` - Close the chat session
- `get_escalations` - Request pending escalations

### Incoming Events (Server → Agent)
- `escalation_pending` - New escalation available
- `chat_message` - New message in chat
- `session_closed` - Session has been closed
- `agent_joined` - Confirmation of joining room
- `agent_left` - Confirmation of leaving room
- `connection_status` - Connection state updates

## Configuration

### Socket Connection
The dashboard connects to the WebSocket server at `http://localhost:3001` by default. To change this:

1. Edit `src/socket.js`
2. Update the `serverUrl` parameter in the `connect()` method
3. Or pass a custom URL when initializing: `socketManager.connect('your-server-url')`

### Agent ID
The default agent ID is `agent_001`. This can be customized in the socket event handlers or made configurable through the UI.

## Usage

### For Agents

1. **Connect**: The dashboard automatically connects to the backend server
2. **View Escalations**: See all pending chats in the left panel
3. **Join Chat**: Click "Join" on any pending escalation
4. **View Summary**: Read the AI-generated summary at the top
5. **Chat with Customer**: Send messages in real-time
6. **Close Session**: Click "Close Session" when done

### For Developers

#### Adding New Components
```javascript
import React from 'react';
import { Box, Typography } from '@mui/material';

const MyComponent = ({ prop1, prop2 }) => {
  return (
    <Box>
      <Typography variant="h6">{prop1}</Typography>
    </Box>
  );
};

export default MyComponent;
```

#### Extending Socket Events
```javascript
// In socket.js
this.socket.on('custom_event', (data) => {
  this.emit('custom_event', data);
});

// In components
socketManager.on('custom_event', (data) => {
  // Handle custom event
});
```

## Styling

The application uses Material UI's theming system with custom CSS enhancements:

- **Theme**: Light theme with primary blue and secondary red colors
- **Typography**: Roboto font family
- **Colors**: Professional color palette with accessibility in mind
- **Responsive**: Mobile-first design with breakpoints

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

### Core
- **React 18.2.0**: UI framework
- **Material UI 5.14.0**: Component library
- **Socket.IO Client 4.7.0**: WebSocket communication

### Development
- **React Scripts 5.0.1**: Build tooling
- **Emotion**: CSS-in-JS styling

## Troubleshooting

### Connection Issues
1. Check if the backend server is running
2. Verify the WebSocket URL in `socket.js`
3. Check browser console for connection errors
4. Ensure firewall/network allows WebSocket connections

### UI Issues
1. Clear browser cache
2. Check for JavaScript errors in console
3. Verify all dependencies are installed
4. Try refreshing the page

### Performance Issues
1. Check network latency to WebSocket server
2. Monitor browser memory usage
3. Close unused browser tabs
4. Monitor system performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the troubleshooting section
- Review the WebSocket event documentation
- Test with the backend server logs
- Contact the development team
