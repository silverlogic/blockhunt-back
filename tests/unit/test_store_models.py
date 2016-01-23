from blockhunt.stores.models import Store, StoreCategory


class TestStore:
    def test_str(self):
        store = Store(name='Dennys')
        assert str(store) == 'Dennys'


class TestStoreCategory:
    def test_str(self):
        category = StoreCategory(name='Restaurants')
        assert str(category) == 'Restaurants'
