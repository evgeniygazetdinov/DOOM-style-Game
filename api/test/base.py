import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = [pytest.mark.django_db]

class Client:
    def __init__(self, user=None):
        self.client = APIClient()
        if user:
            # Delete any existing tokens for this user
            Token.objects.filter(user=user).delete()
            # Create new token
            token = Token.objects.create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def __getattr__(self, name):
        return getattr(self.client, name)


@pytest.fixture
@pytest.mark.django_db
def test_user():
    user = User.objects.create_user(
        username="test@example.com",
        password="testpass123"
    )
    user.profile.id_type = 'email'
    user.profile.save()
    return user
