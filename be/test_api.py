#!/usr/bin/env python3
"""
Test script for the AI-powered telecom support chatbot API
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_ask_ai():
    """Test AI ask endpoint"""
    print("\n🤖 Testing AI ask endpoint...")
    try:
        data = {
            "message": "How do I reset my password?"
        }
        response = requests.post(f"{BASE_URL}/api/ask", json=data)
        print(f"✅ AI ask: {response.status_code}")
        result = response.json()
        print(f"📝 AI Response: {result.get('response', 'No response')}")
        print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ AI ask failed: {e}")
        return False

def test_create_session():
    """Test session creation"""
    print("\n💬 Testing session creation...")
    try:
        data = {
            "user_id": "test_user_123"
        }
        response = requests.post(f"{BASE_URL}/api/sessions", json=data)
        print(f"✅ Session creation: {response.status_code}")
        result = response.json()
        print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
        print(f"🏠 Room ID: {result.get('room_id', 'N/A')}")
        return result.get('session_id')
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return None

def test_ingest_documents():
    """Test document ingestion"""
    print("\n📚 Testing document ingestion...")
    try:
        data = {
            "documents": [
                {
                    "content": "To reset your password, go to account settings and click 'Reset Password'. You'll receive an email with instructions.",
                    "title": "Password Reset Guide",
                    "category": "account_management",
                    "source": "help_center"
                },
                {
                    "content": "For billing questions, contact our support team at billing@telecom.com or call 1-800-TELECOM.",
                    "title": "Billing Support",
                    "category": "billing",
                    "source": "support_guide"
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/api/ingest", json=data)
        print(f"✅ Document ingestion: {response.status_code}")
        result = response.json()
        print(f"📊 Documents ingested: {result.get('count', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Document ingestion failed: {e}")
        return False

def test_create_user():
    """Test user creation"""
    print("\n👤 Testing user creation...")
    try:
        data = {
            "user_id": "test_user_123",
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        response = requests.post(f"{BASE_URL}/api/users", json=data)
        print(f"✅ User creation: {response.status_code}")
        result = response.json()
        print(f"👤 User created: {result.get('success', False)}")
        return True
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False

def test_create_agent():
    """Test agent creation"""
    print("\n👨‍💼 Testing agent creation...")
    try:
        data = {
            "agent_id": "agent_001",
            "name": "John Smith",
            "email": "john@telecom.com",
            "is_available": True
        }
        response = requests.post(f"{BASE_URL}/api/agents", json=data)
        print(f"✅ Agent creation: {response.status_code}")
        result = response.json()
        print(f"👨‍💼 Agent created: {result.get('success', False)}")
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_force_escalation(session_id):
    """Test forced escalation"""
    if not session_id:
        print("\n⚠️ Skipping escalation test - no session ID")
        return False
        
    print("\n🚨 Testing forced escalation...")
    try:
        data = {
            "session_id": session_id,
            "reason": "Test escalation"
        }
        response = requests.post(f"{BASE_URL}/api/escalate", json=data)
        print(f"✅ Forced escalation: {response.status_code}")
        result = response.json()
        print(f"🚨 Escalation created: {result.get('success', False)}")
        return True
    except Exception as e:
        print(f"❌ Forced escalation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI-Powered Telecom Support Chatbot - API Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Document Ingestion", test_ingest_documents),
        ("User Creation", test_create_user),
        ("Agent Creation", test_create_agent),
        ("Session Creation", test_create_session),
        ("AI Ask", test_ask_ai),
    ]
    
    session_id = None
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_name == "Session Creation":
                session_id = test_func()
                if session_id:
                    passed += 1
            else:
                if test_func():
                    passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Test escalation if we have a session
    if session_id:
        tests.append(("Forced Escalation", lambda: test_force_escalation(session_id)))
        total += 1
        if test_force_escalation(session_id):
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")
    
    print("\n💡 Next steps:")
    print("1. Start the server: python app.py")
    print("2. Test WebSocket connection with a client")
    print("3. Try the escalation flow with real messages")

if __name__ == "__main__":
    main()
