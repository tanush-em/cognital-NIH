#!/usr/bin/env python3
"""
Simple WebSocket test to verify chat functionality
"""
import socketio
import time
import json

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to server")

@sio.event
def disconnect():
    print("❌ Disconnected from server")

@sio.event
def connected(data):
    print(f"📡 Server response: {data}")

@sio.event
def new_message(data):
    print(f"🤖 AI Response: {data['content']}")
    print(f"📊 Confidence: {data.get('confidence', 'N/A')}")

@sio.event
def escalation_triggered(data):
    print(f"🚨 Escalation triggered: {data}")

def test_chat():
    try:
        # Connect to the server
        print("🔌 Connecting to WebSocket server...")
        sio.connect('http://localhost:5000')
        
        # Wait a moment for connection
        time.sleep(1)
        
        # Join a session
        session_id = f"session_test_{int(time.time())}"
        print(f"📝 Joining session: {session_id}")
        sio.emit('join_session', {'sessionId': session_id})
        
        # Wait a moment
        time.sleep(1)
        
        # Send a test message using user_message
        print("💬 Sending test message: 'hi'")
        sio.emit('user_message', {
            'sessionId': session_id,
            'message': 'hi',
            'messageType': 'user',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        })
        
        # Wait for response
        print("⏳ Waiting for AI response...")
        time.sleep(5)
        
        # Send another message
        print("💬 Sending test message: 'What can you help me with?'")
        sio.emit('user_message', {
            'sessionId': session_id,
            'message': 'What can you help me with?',
            'messageType': 'user',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        })
        
        # Wait for response
        print("⏳ Waiting for AI response...")
        time.sleep(5)
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        # Disconnect
        sio.disconnect()
        print("🔌 Disconnected from server")

if __name__ == "__main__":
    test_chat()
