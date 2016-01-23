from blockhunt.users.models import User


class TestUser:
    def test_get_short_name(self):
        user = User(first_name='John', last_name='Smith')
        assert user.get_short_name() == 'John Smith'

    def test_get_full_name(self):
        user = User(first_name='John', last_name='Smith')
        assert user.get_full_name() == 'John Smith'
