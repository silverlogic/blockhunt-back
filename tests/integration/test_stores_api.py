from django.contrib.gis.geos import Point

import pytest

from blockhunt.stores.models import StoreOwner, Store, StoreAddress

import tests.factories as f
import tests.helpers as h
from tests.mixins import ApiMixin


pytestmark = pytest.mark.django_db


class TestStoreCreate(ApiMixin):
    view_name = 'store-list'

    @pytest.fixture
    def data(self, image):
        category = f.StoreCategoryFactory()
        return {
            'email': 'ry@tsl.io',
            'password': 'blub',
            'store_name': 'The Pub',
            'category': category.pk,
            'address': {
                'line1': '400 NW 26th St',
                'zip_code': '33127',
                'city': 'Miami',
                'state': 'Florida',
                'country': 'us'
            },
            'photo': image,
            'website': 'https://google.ca',
            'bounty': '0.001'
        }

    def test_guest_can_create(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)

    def test_creates_store_owner(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        assert StoreOwner.objects.count() == 1

    def test_sets_store_owner_password(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        assert StoreOwner.objects.get().check_password(data['password'])

    def test_creates_store(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        assert Store.objects.count() == 1

    def test_creates_store_address(self, client, data):
        r = client.post(self.reverse(), data)
        h.responseCreated(r)
        assert StoreAddress.objects.count() == 1

    def test_geocodes_store_address(self, client, data):
        pass

    def test_email_cant_already_be_taken(self, client, data):
        f.StoreOwnerFactory(email=data['email'])
        r = client.post(self.reverse(), data)
        h.responseBadRequest(r)
        assert r.data['email'] == ['That email address is already in use.']


class TestStoreList(ApiMixin):
    view_name = 'store-list'

    def test_guest_can_list(self, client):
        r = client.get(self.reverse())
        h.responseOk(r)

    def test_hunter_can_list(self, hunter_client):
        r = hunter_client.get(self.reverse())
        h.responseOk(r)

    def test_store_owner_can_list(self, store_owner_client):
        r = store_owner_client.get(self.reverse())
        h.responseOk(r)

    def test_sorts_by_distance_when_coords_are_provided(self, hunter_client, client):
        farthest = f.StoreFactory(address=True, address__coords=Point(200, 200))
        closest = f.StoreFactory(address=True, address__coords=Point(51, 51))
        medium = f.StoreFactory(address=True, address__coords=Point(100, 100))
        r = hunter_client.get(self.reverse(query_params={'coords': '50,50'}))
        h.responseOk(r)
        assert r.data['count'] == 3
        results = r.data['results']
        assert results[0]['id'] == closest.pk
        assert results[1]['id'] == medium.pk
        assert results[2]['id'] == farthest.pk

    def test_coords_can_be_negative(self, hunter_client, client):
        f.StoreFactory(address=True, address__coords=Point(100, 100))
        r = hunter_client.get(self.reverse(query_params={'coords': '-50,-50'}))
        h.responseOk(r)
        results = r.data['results']
        assert results[0]['distance'] is not None

    def test_includes_distance_field_on_results(self, hunter_client, client):
        f.StoreFactory(address=True, address__coords=Point(100, 100))
        r = hunter_client.get(self.reverse(query_params={'coords': '50,50'}))
        h.responseOk(r)
        results = r.data['results']
        assert results[0]['distance'] is not None

    def test_doesnt_explode_if_bad_coords(self, hunter_client, client):
        f.StoreFactory()
        f.StoreFactory()
        f.StoreFactory()
        r = hunter_client.get(self.reverse(query_params={'coords': 'asd'}))
        h.responseOk(r)
        assert r.data['count'] == 3


class TestStoreRetrieve(ApiMixin):
    view_name = 'store-detail'

    def test_guest_can_retrieve(self, client):
        store = f.StoreFactory()
        r = client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)

    def test_hunter_can_retrieve(self, hunter_client):
        store = f.StoreFactory()
        r = hunter_client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)

    def test_store_owner_can_retrieve(self, store_owner_client):
        store = f.StoreFactory()
        r = store_owner_client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)

    def test_object_keys(self, hunter_client):
        store = f.StoreFactory()
        r = hunter_client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)
        expected = {'id', 'name', 'category', 'address', 'photo', 'website', 'tagline',
                    'distance', 'bounty'}
        actual = set(r.data.keys())
        assert expected == actual

    def test_address_object_keys(self, hunter_client):
        store = f.StoreFactory()
        f.StoreAddressFactory(store=store)
        r = hunter_client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)
        expected = {'line1', 'line2', 'line3', 'zip_code', 'city', 'state', 'country', 'coords'}
        actual = set(r.data['address'].keys())
        assert expected == actual

    def test_address_coords_object_keys(self, hunter_client):
        store = f.StoreFactory()
        f.StoreAddressFactory(store=store)
        r = hunter_client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)
        expected = {'lat', 'long'}
        actual = set(r.data['address']['coords'].keys())
        assert expected == actual

    def test_photo_object_keys(self, hunter_client):
        store = f.StoreFactory()
        r = hunter_client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseOk(r)
        expected = {'url'}
        actual = set(r.data['photo'].keys())
        assert expected == actual

    def test_category_is_expandable(self, hunter_client):
        store = f.StoreFactory()
        r = hunter_client.get(self.reverse(kwargs={'pk': store.pk}, query_params={'expand': 'category'}))
        h.responseOk(r)
        assert isinstance(r.data['category'], dict)


class TestStoreCategoryRetrieve(ApiMixin):
    view_name = 'storecategory-detail'

    def test_guest_can_retrieve(self, client):
        category = f.StoreCategoryFactory()
        r = client.get(self.reverse(kwargs={'pk': category.pk}))
        h.responseOk(r)

    def test_hunter_can_retrieve(self, hunter_client):
        category = f.StoreCategoryFactory()
        r = hunter_client.get(self.reverse(kwargs={'pk': category.pk}))
        h.responseOk(r)

    def test_store_owner_can_retrieve(self, store_owner_client):
        category = f.StoreCategoryFactory()
        r = store_owner_client.get(self.reverse(kwargs={'pk': category.pk}))
        h.responseOk(r)


class TestStoreCategoryList(ApiMixin):
    view_name = 'storecategory-list'

    def test_guest_can_list(self, client):
        r = client.get(self.reverse())
        h.responseOk(r)

    def test_hunter_can_list(self, hunter_client):
        r = hunter_client.get(self.reverse())
        h.responseOk(r)

    def test_store_owner_can_retrieve(self, store_owner_client):
        r = store_owner_client.get(self.reverse())
        h.responseOk(r)
