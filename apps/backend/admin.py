from django.contrib import admin
from backend.models import Item, Price

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rs_id', 'members', 'examine')
    list_filter = ('members',)
    search_fields = ['name', 'rs_id']

class PriceAdmin(admin.ModelAdmin):
    list_display = ('item', 'day', 'min_price', 'price', 'max_price', 'volume', 'seven_day_volume')
    raw_id_fields = ['item']

admin.site.register(Item, ItemAdmin)
admin.site.register(Price, PriceAdmin)
