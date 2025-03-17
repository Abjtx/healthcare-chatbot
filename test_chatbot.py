#!/usr/bin/env python3
import requests
import json
import time
import sys

def test_rasa_server():
    """Test if Rasa server is running"""
    try:
        response = requests.get("http://localhost:5005/")
        if response.status_code == 200:
            print("✅ Rasa server is running")
            return True
        else:
            print("❌ Rasa server returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Rasa server is not running")
        return False

def test_actions_server():
    """Test if Rasa Actions server is running"""
    try:
        response = requests.get("http://localhost:5055/health")
        if response.status_code == 200:
            print("✅ Rasa Actions server is running")
            return True
        else:
            print("❌ Rasa Actions server returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Rasa Actions server is not running")
        return False

def test_flask_api():
    """Test if Flask API is running"""
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ Flask API is running")
            return True
        else:
            print("❌ Flask API returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask API is not running")
        return False

def test_chat_functionality():
    """Test the chat functionality"""
    try:
        # Test a greeting
        payload = {
            "message": "Hello",
            "user_id": "test_user"
        }
        response = requests.post("http://localhost:8000/api/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "messages" in data and len(data["messages"]) > 0:
                print("✅ Chat functionality is working")
                print("Bot response:", data["messages"][0]["text"])
                return True
            else:
                print("❌ Chat functionality returned empty response")
                return False
        else:
            print("❌ Chat functionality returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to chat API")
        return False
    except Exception as e:
        print("❌ Error testing chat functionality:", str(e))
        return False

def main():
    print("Testing Healthcare Chatbot Setup...")
    print("-" * 40)
    
    # Wait a bit for services to start
    print("Waiting for services to start...")
    time.sleep(15)  # Increased wait time to 15 seconds
    
    rasa_ok = test_rasa_server()
    actions_ok = test_actions_server()
    flask_ok = test_flask_api()
    
    if rasa_ok and actions_ok and flask_ok:
        print("-" * 40)
        print("Testing chat functionality...")
        chat_ok = test_chat_functionality()
        
        if chat_ok:
            print("-" * 40)
            print("✅ All tests passed! The chatbot is working correctly.")
            return 0
        else:
            print("-" * 40)
            print("❌ Chat functionality test failed.")
            return 1
    else:
        print("-" * 40)
        print("❌ One or more services are not running correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 