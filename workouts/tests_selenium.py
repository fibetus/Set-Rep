import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth.models import User
from django.test import LiveServerTestCase

class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        # Clear any existing users
        User.objects.all().delete()

    def test_register_and_login(self):
        # Test registration
        self.selenium.get(f'{self.live_server_url}/register.html')
        
        # Fill in registration form
        email_input = self.selenium.find_element(By.NAME, 'email')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        test_email = 'test@example.com'
        test_password = 'testpass123'
        
        email_input.send_keys(test_email)
        password_input.send_keys(test_password)
        submit_button.click()
        
        # Wait for redirect to login page
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('login.html')
        )
        
        # Test login
        email_input = self.selenium.find_element(By.NAME, 'email')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        email_input.send_keys(test_email)
        password_input.send_keys(test_password)
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('dashboard.html')
        )
        
        # Verify user was created in database
        self.assertTrue(User.objects.filter(email=test_email).exists())

    def test_register_duplicate_email(self):
        # Create a user first
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Try to register with same email
        self.selenium.get(f'{self.live_server_url}/register.html')
        
        email_input = self.selenium.find_element(By.NAME, 'email')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        email_input.send_keys('existing@example.com')
        password_input.send_keys('testpass123')
        submit_button.click()
        
        # Wait for error message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        
        # Verify we're still on register page
        self.assertIn('register.html', self.selenium.current_url)

    def test_login_invalid_credentials(self):
        self.selenium.get(f'{self.live_server_url}/login.html')
        
        email_input = self.selenium.find_element(By.NAME, 'email')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        email_input.send_keys('nonexistent@example.com')
        password_input.send_keys('wrongpass')
        submit_button.click()
        
        # Wait for error message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        
        # Verify we're still on login page
        self.assertIn('login.html', self.selenium.current_url) 