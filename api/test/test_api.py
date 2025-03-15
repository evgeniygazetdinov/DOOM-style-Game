import pytest
from django.urls import reverse
import responses

from api.test.base import Client


@pytest.mark.django_db
class TestAPIEndpoints:
    def test_info_endpoint(self, test_user):
        client = Client(user=test_user)
        response = client.get(reverse('info'))
        assert response.status_code == 200
        assert response.data['id'] == test_user.username
        assert response.data['id_type'] == 'email'

    @responses.activate
    def test_latency_endpoint(self, test_user):
        client = Client(user=test_user)
        responses.add(
            responses.GET,
            'https://ya.ru',
            status=200,
            body='OK'
        )
        
        response = client.get(reverse('latency'))
        assert response.status_code == 200
        assert 'latency_ms' in response.data
        assert isinstance(response.data['latency_ms'], float)