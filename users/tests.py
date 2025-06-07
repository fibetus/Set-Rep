from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

# Create your tests here.

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:register_user')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123'
        }

    def test_register_user_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='existing@test.com',
            password='testpass123'
        )
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='test@test.com',
            password='testpass123'
        )
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_register_user_missing_fields(self):
        """Test registration with missing fields"""
        payload = {
            'username': 'testuser',
            'email': 'test@test.com'
            # password missing
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_register_user_weak_password(self):
        """Test registration with weak password"""
        payload = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': '123'  # too short
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

class UserLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            username='test@test.com',  # Using email as username
            email='test@test.com',
            password='testpass123'
        )

    def test_login_success(self):
        """Test successful login"""
        payload = {
            'username': 'test@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        payload = {
            'username': 'test@test.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        payload = {
            'username': 'nonexistent@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        payload = {
            'username': 'test@test.com'
            # password missing
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
