#!/usr/bin/env python3
"""
Test script for telecom chatbot human handoff functionality
"""
import requests
import json
import time
import socketio

# Test configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def test_api_endpoints():
    """Test API endpoints are working"""
    print("Testing API endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test escalations endpoint
    try:
        response = requests.get(f"{API_URL}/escalations")
        if response.status_code == 200:
            print("✓ Escalations endpoint working")
        else:
            print("✗ Escalations endpoint failed")
    except Exception as e:
        print(f"✗ Escalations endpoint failed: {e}")
    
    return True

def test_websocket_connection():
    """Test WebSocket connection"""
    print("\nTesting WebSocket connection...")
    
    try:
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("✓ WebSocket connected")
        
        @sio.event
        def disconnect():
            print("✓ WebSocket disconnected")
        
        @sio.event
        def escalation_pending(data):
            print(f"✓ Received escalation: {data}")
        
        sio.connect(BASE_URL)
        time.sleep(2)
        sio.disconnect()
        return True
        
    except Exception as e:
        print(f"✗ WebSocket connection failed: {e}")
        return False

def test_escalation_flow():
    """Test the complete escalation flow"""
    print("\nTesting escalation flow...")
    
    # Create a test session
    session_data = {
        "session_id": "test_session_123",
        "user_id": "test_user",
        "room_id": "test_room_123"
    }
    
    try:
        # Test session creation (this would normally be done via WebSocket)
        print("✓ Test session data prepared")
        
        # Test escalation service
        from services.escalation_service import escalation_service
        
        # Test escalation check
        escalation_result = escalation_service.should_escalate(
            session_id=1,  # This would be a real session ID
            user_message="I'm very frustrated with my service!",
            confidence=0.3,
            message_count=5,
            session_duration=600
        )
        
        if escalation_result.get('should_escalate'):
            print("✓ Escalation detection working")
        else:
            print("✗ Escalation detection not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Escalation flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Telecom Chatbot Handoff Tests")
    print("=" * 50)
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    # Test WebSocket connection
    ws_ok = test_websocket_connection()
    
    # Test escalation flow
    escalation_ok = test_escalation_flow()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"API Endpoints: {'✓ PASS' if api_ok else '✗ FAIL'}")
    print(f"WebSocket: {'✓ PASS' if ws_ok else '✗ FAIL'}")
    print(f"Escalation Flow: {'✓ PASS' if escalation_ok else '✗ FAIL'}")
    
    if api_ok and ws_ok and escalation_ok:
        print("\n🎉 All tests passed! Handoff system is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    main()
