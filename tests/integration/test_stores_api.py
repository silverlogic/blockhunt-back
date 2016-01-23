import pytest

import tests.factories as f
import tests.helpers as h
from tests.mixins import ApiMixin


pytestmark = pytest.mark.django_db


# class TestStoreCreate(ApiMixin):
#     view_name = 'store-list'

#     @pytest.fixture
#     def data(self, image):
#         category = f.StoreCategoryFactory()
#         return {
#             'name': 'Dennys',
#             'photo': image,
#             'category': category.pk,
#         }

#     def test_guest_cant_create(self, client, data):
#         r = client.post(self.reverse(), data)
#         h.responseUnauthorized(r)

#     def test_store_owner_can_create(self, store_owner_client):
#         pass


class TestStoreList(ApiMixin):
    view_name = 'store-list'

    def test_guest_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_store_owner_can_list(self, store_owner_client):
        r = store_owner_client.get(self.reverse())
        h.responseOk(r)


class TestStoreRetrieve(ApiMixin):
    view_name = 'store-detail'

    def test_guest_cant_retrieve(self, client):
        store = f.StoreFactory()
        r = client.get(self.reverse(kwargs={'pk': store.pk}))
        h.responseUnauthorized(r)

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
        expected = {'id', 'name', 'category', 'address', 'photo', 'website', 'tagline'}
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


class TestStoreCategoryList(ApiMixin):
    view_name = 'storecategory-list'

    def test_guest_cant_list(self, client):
        r = client.get(self.reverse())
        h.responseUnauthorized(r)

    def test_hunter_can_list(self, hunter_client):
        r = hunter_client.get(self.reverse())
        h.responseOk(r)

    def test_store_owner_can_retrieve(self, store_owner_client):
        r = store_owner_client.get(self.reverse())
        h.responseOk(r)
