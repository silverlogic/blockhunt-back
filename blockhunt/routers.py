from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)


# Stores
from blockhunt.stores.api import StoreViewSet, StoreCategoryViewSet  # noqa
router.register(r'stores', StoreViewSet)
router.register(r'store-categories', StoreCategoryViewSet)
