from django.contrib import admin

from .models import Store, StoreAddress, StoreCategory, StoreOwner


class StoreAddressInline(admin.StackedInline):
    model = StoreAddress


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    model = Store
    inlines = [StoreAddressInline]
    readonly_fields = ('balance',)


@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    model = StoreCategory


@admin.register(StoreOwner)
class StoreOwnerAdmin(admin.ModelAdmin):
    model = StoreOwner
