from decimal import Decimal

import pytest

import tests.factories as f
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


class TestCheckinCreate(ApiMixin):
    view_name = 'checkin-list'

    @pytest.fixture
    def data(self):
        self.store = f.StoreFactory(bounty=1, balance=1)
        return {
            'qrcode': self.store.pk,
            'coords': {
                'lat': 11,
                'long': 11
            }
        }

    def test_guest_cant_create(self, client):
        r = client.post(self.reverse())
        h.responseUnauthorized(r)

    def test_hunter_can_create(self, hunter_client, data):
        r = hunter_client.post(self.reverse(), data)
        h.responseCreated(r)

    def test_removes_bitcoins_from_stores_balance(self, hunter_client, data):
        r = hunter_client.post(self.reverse(), data)
        h.responseCreated(r)
        self.store.refresh_from_db()
        assert self.store.balance == Decimal(0)

    def test_adds_bitcoins_to_hunters_balance(self, hunter_client, data):
        r = hunter_client.post(self.reverse(), data)
        h.responseCreated(r)
        self.store.refresh_from_db()
        hunter_client.user.refresh_from_db()
        assert hunter_client.user.balance == Decimal(1)

    def test_store_must_have_enough_bitcoins(self, hunter_client, data):
        self.store.balance = 0.5
        self.store.save()
        r = hunter_client.post(self.reverse(), data)
        h.responseBadRequest(r)
        assert r.data['qrcode'] == ['Unfortunately the store does not have enough bitcoins to pay the bounty.']


class TestCheckinRetrieve(ApiMixin):
    view_name = 'checkin-detail'

    def test_guest_cant_retrieve(self, client):
        checkin = f.CheckinFactory()
        r = client.get(self.reverse(kwargs={'pk': checkin.pk}))
        h.responseUnauthorized(r)

    def test_hunter_cant_retrieve_other_hunters(self, hunter_client):
        checkin = f.CheckinFactory()
        r = hunter_client.get(self.reverse(kwargs={'pk': checkin.pk}))
        h.responseNotFound(r)

    def test_hunter_can_retrieve_own(self, hunter_client):
        checkin = f.CheckinFactory(hunter=hunter_client.user)
        r = hunter_client.get(self.reverse(kwargs={'pk': checkin.pk}))
        h.responseOk(r)

    def test_object_keys(self, hunter_client):
        checkin = f.CheckinFactory(hunter=hunter_client.user)
        r = hunter_client.get(self.reverse(kwargs={'pk': checkin.pk}))
        h.responseOk(r)
        expected = {'id', 'store', 'reward'}
        actual = set(r.data.keys())
        assert expected == actual

    def test_can_expand_store(self, hunter_client):
        checkin = f.CheckinFactory(hunter=hunter_client.user)
        r = hunter_client.get(self.reverse(kwargs={'pk': checkin.pk}, query_params={'expand': 'store'}))
        h.responseOk(r)
        print(r.data)
        assert isinstance(r.data['store'], dict)


class TestCheckinList(ApiMixin):
    view_name = 'checkin-list'

    def test_guest_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_hunter_can_list(self, hunter_client):
        r = hunter_client.get(self.reverse())
        h.responseOk(r)
