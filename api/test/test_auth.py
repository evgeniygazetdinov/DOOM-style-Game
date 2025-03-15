import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from freezegun import freeze_time
from datetime import datetime, timedelta
from .base import Client, test_user

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    def test_signup_with_email(self):
        data = {
            "id": "new@example.com",
            "password": "testpass123"
        }
        response = Client().post(reverse('signup'), data, format='json')
        assert response.status_code == 201
        assert 'token' in response.data
        assert 'expires_in' in response.data
        assert response.data['expires_in'] == 300

    def test_signup_with_phone(self):
        data = {
            "id": "+79123456789",
            "password": "testpass123"
        }
        response = Client().post(reverse('signup'), data, format='json')
        assert response.status_code == 201
        assert 'token' in response.data

    def test_signin_success(self, test_user):
        data = {
            "id": "test@example.com",
            "password": "testpass123"
        }
        response = Client().post(reverse('signin'), data, format='json')
        assert response.status_code == 200
        assert 'token' in response.data
        assert 'expires_in' in response.data

    @pytest.mark.django_db
    def test_token_expiry(self, test_user):
        client = Client(user=test_user)
        current_time = datetime(2025, 3, 14, 10, 0, 0)
        with freeze_time(current_time):
            response = client.get(reverse('info'))
            assert response.status_code == 200

        with freeze_time(current_time + timedelta(minutes=10)):
            response = client.get(reverse('info'))
            assert response.status_code == 401
            assert 'Token has expired' in str(response.json().get('error'))

    @pytest.mark.django_db
    def test_token_renewal(self, test_user):
        Token.objects.filter(user=test_user).delete()
        
        current_time = datetime(2025, 3, 14, 10, 0, 0)
        with freeze_time(current_time):
            response = Client(user=test_user).get(reverse('info'))
            assert response.status_code == 200

        with freeze_time(current_time + timedelta(minutes=4)):
            response = Client(user=test_user).get(reverse('info'))
            assert response.status_code == 200
            token = Token.objects.get(user=test_user)
            assert token.created.timestamp() == (current_time + timedelta(minutes=4)).timestamp()

    @pytest.mark.django_db
    def test_logout_single_session(self, test_user):
        Token.objects.filter(user=test_user).delete()
        response = Client(user=test_user).post(reverse('logout'), {'all': False}, format='json')
        assert response.status_code == 200
        assert not Token.objects.filter(user=test_user).exists()

    @pytest.mark.django_db
    def test_logout_all_sessions(self, test_user):
        client = Client(user=test_user)
        Token.objects.filter(user=test_user).delete()
        # Create token
        token = Token.objects.create(user=test_user)

        response = client.post(reverse('logout'), {'all': True}, format='json')
        assert response.status_code == 200
        assert not Token.objects.filter(user=test_user).exists()