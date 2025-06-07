import requests
import json

BASE_URL = 'http://localhost:8000'

def test_registration_and_login():
    # Test data
    test_user = {
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'testpass123'
    }

    # Step 1: Register user
    print("Testing registration...")
    register_response = requests.post(
        f'{BASE_URL}/api/v1/users/register/',
        json=test_user
    )
    print(f"Registration response: {register_response.status_code}")
    print(json.dumps(register_response.json(), indent=2))

    # Step 2: Try to login
    print("\nTesting login...")
    login_data = {
        'username': test_user['email'],  # Use email as username
        'password': test_user['password']
    }
    login_response = requests.post(
        f'{BASE_URL}/api/v1/auth/token/',
        json=login_data
    )
    print(f"Login response: {login_response.status_code}")
    print(json.dumps(login_response.json(), indent=2))

    return register_response.status_code == 201 and login_response.status_code == 200

if __name__ == '__main__':
    success = test_registration_and_login()
    print(f"\nTest {'passed' if success else 'failed'}") 