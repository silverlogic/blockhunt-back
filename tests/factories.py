from django.contrib.gis.geos import Point
import factory
import factory.fuzzy


class UserFactory(factory.DjangoModelFactory):
    email = factory.fuzzy.FuzzyText(length=20, suffix='@test.com')
    password = factory.PostGenerationMethodCall('set_password', 'default_password')
    first_name = factory.fuzzy.FuzzyText(length=10)
    last_name = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = 'users.User'


class StoreOwnerFactory(UserFactory):
    class Meta:
        model = 'stores.StoreOwner'


class StoreFactory(factory.DjangoModelFactory):
    owner = factory.SubFactory('tests.factories.StoreOwnerFactory')
    name = factory.fuzzy.FuzzyText(length=25)
    photo = factory.django.ImageField()
    category = factory.SubFactory('tests.factories.StoreCategoryFactory')
    website = 'https://dennys.com'

    class Meta:
        model = 'stores.Store'

    @factory.post_generation
    def address(self, create, extracted, **kwargs):
        if extracted:
            StoreAddressFactory(store=self, **kwargs)


class StoreCategoryFactory(factory.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)
    icon = factory.django.ImageField()

    class Meta:
        model = 'stores.StoreCategory'


class StoreAddressFactory(factory.DjangoModelFactory):
    store = factory.SubFactory('tests.factories.StoreFactory')
    line1 = factory.fuzzy.FuzzyText(length=30)
    zip_code = 90210
    city = 'Miami'
    state = 'Florida'
    country = 'United States'
    coords = Point(0, 0)

    class Meta:
        model = 'stores.StoreAddress'
