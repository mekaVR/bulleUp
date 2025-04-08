from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse_lazy, reverse

User = get_user_model()

class UsersAPIViewsTest(APITestCase):

    def test_register_api_view_is_working(self):
        url = reverse('user-register')
        body = {'email': 'user@email.com', 'password': 'Password1', 'username': 'test-user'}
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.filter(email=body['email']).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(body['password']))

    def test_register_api_view_no_double_emails(self):
        user = User.objects.create_user(email='user@email.com', password='Password1', username='test-user')
        url = reverse('user-register')
        body = {'email': 'user@email.com', 'password': 'Password1', 'username': 'test-user'}
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_api_view_password_validation(self):
        url = reverse('user-register')
        body = {'email': 'user@email.com', 'password': 'passwor', 'username': 'test-user'}
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, 400)