from django.contrib import admin

from .models import Hunter, Checkin


@admin.register(Hunter)
class HunterAdmin(admin.ModelAdmin):
    model = Hunter
    readonly_fields = ('balance',)


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    model = Checkin
