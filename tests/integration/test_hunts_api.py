import pytest

import tests.helpers as h
from tests.mixins import ApiMixin

from blockhunt.hunts.models import Hunter


pytestmark = pytest.mark.django_db


class TestHunterCreate(ApiMixin):
    view_name = 'hunter-list'

    @pytest.fixture
    def data(self):
        return {
            'email': 'bobby@rockstar.ca',
            'password': '1234'
        }

    def test_can_create(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)

    def test_password_is_set(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        hunter = Hunter.objects.get()
        assert hunter.check_password(data['password'])

    def test_name_is_assigned_randomly_if_not_provided(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        hunter = Hunter.objects.get()
        assert hunter.first_name
        assert hunter.last_name

    def test_can_set_name(self, client, data):
        data['first_name'] = 'Bob'
        data['last_name'] = 'Rock'
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        hunter = Hunter.objects.get()
        assert hunter.first_name == data['first_name']
        assert hunter.last_name == data['last_name']


class TestHunterSelfRetrieve(ApiMixin):
    view_name = 'hunter-self-list'

    def test_guest_cant_retrieve(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_hunter_can_retrieve(self, hunter_client):
        r = hunter_client.get(self.reverse())
        h.responseOk(r)

    def test_object_keys(self, hunter_client):
        r = hunter_client.get(self.reverse())
        h.responseOk(r)
        expected = {'id', 'email', 'first_name', 'last_name'}
        actual = set(r.data.keys())
        assert expected == actual
