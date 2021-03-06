from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)


# Stores
from blockhunt.stores.api import StoreViewSet, StoreCategoryViewSet, \
    CoinbaseNotificationViewSet  # noqa

router.register(r'stores', StoreViewSet)
router.register(r'store-categories', StoreCategoryViewSet)
router.register(r'coinbase-notifications', CoinbaseNotificationViewSet, base_name='coinbase-notification')


# Hunts
from blockhunt.hunts.api import HunterViewSet, HunterSelfViewSet, \
    CheckinViewSet  # noqa

router.register(r'hunters', HunterViewSet)
router.register(r'hunter', HunterSelfViewSet, base_name='hunter-self')
router.register(r'checkins', CheckinViewSet)
