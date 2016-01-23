from io import BytesIO

from django.core.files.images import ImageFile

import pytest
from rest_framework.test import APIClient

from tests import factories as f


class Client(APIClient):
    def force_authenticate(self, user):
        self.user = user
        super().force_authenticate(user)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def hunter_client():
    hunter = f.HunterFactory()
    client = Client()
    client.force_authenticate(hunter)
    return client


@pytest.fixture
def store_owner_client():
    store_owner = f.StoreOwnerFactory()
    client = Client()
    client.force_authenticate(store_owner)
    return client


@pytest.fixture
def outbox():
    from django.core import mail
    return mail.outbox


@pytest.fixture
def image():
    return 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAMAAAAM7l6QAAAARVBMVEXPACr///8HAAIVAARnND5oABVzABcnCA6mACJHAA62ACXhztGcbXfi0dVzP0qZAB86EhqLWWPNsLZUABEjAAcaBAhbKjRAQ1vHAAAA+0lEQVQokYWTCZKEIAxFw2cTV9z6/kftsMjoiG2qVPQlAZMfEod1vfI7sHvVd+Uj5ecyWhSz43LFM0Pp9NS2k3aSHeYTHhSw6YayNZod1HDg4QO4AqPDCnyGjDnW0D/jBCrhuUKZA3PAi8V6p0Qr7MJ4hGxquNkwCuosdI2G9Laj/iGYwyV6UnC8FFeSXh0U+Zi7ig087Zgoli7eiY4m8GqCJKDN7ukSf9EtcMZHjjOOyUt03jktQ3KfKpr3FuUA+Wjpx6oWfuylLC9F5ZZsP1ry1tAHOZgshyAmeeOmiClKcX2W4l3I21nIZQxMGANzG4PXIcojyHHyMoJf+KcJUmsQs8MAAAAASUVORK5CYII='


@pytest.fixture
def image_file(image):
    i = BytesIO(image.encode('utf-8'))
    return ImageFile(i, name='image.png')
