from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

class AuthFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:register_user')
        self.login_url = reverse('token_obtain_pair')
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123'
        }

    def test_registration_and_login_flow(self):
        """Test the complete registration and login flow"""
        
        # Step 1: Register user
        print("Testing registration...")
        register_response = self.client.post(
            self.register_url,
            self.test_user_data,
            format='json'
        )
        print(f"Registration response: {register_response.status_code}")
        print(f"Registration data: {register_response.data}")

        # Assert registration was successful
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # Step 2: Try to login with username (not email)
        print("\nTesting login...")
        login_data = {
            'username': 'testuser',  # Use username, not email
            'password': 'testpass123'
        }
        login_response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )
        print(f"Login response: {login_response.status_code}")
        print(f"Login data: {login_response.data}")

        # Assert login was successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_registration_duplicate_user(self):
        """Test registration with duplicate user data"""
        # Create user first
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Try to register the same user again
        register_response = self.client.post(
            self.register_url,
            self.test_user_data,
            format='json'
        )
        
        # Should fail with 400
        self.assertEqual(register_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', register_response.data)

    def test_login_with_registered_user(self):
        """Test login with a pre-registered user"""
        # Create user first with username as 'testuser'
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Try to login with username
        login_data = {
            'username': 'testuser',  # Use username, not email
            'password': 'testpass123'
        }
        login_response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )
        
        # Should succeed
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data) 