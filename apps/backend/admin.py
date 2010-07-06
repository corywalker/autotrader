from django.contrib import admin
from backend.models import Item, Price, Potential, Update

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rs_id', 'members', 'examine', 'get_sprite_html')
    list_filter = ('members',)
    search_fields = ['name', 'rs_id']

class PriceAdmin(admin.ModelAdmin):
    list_display = ('item', 'update', 'min_price', 'price', 'max_price', 'volume', 'seven_day_volume')
    list_filter = ('update',)
    raw_id_fields = ['item', 'update']
    search_fields = ['item__name']

class PotentialAdmin(admin.ModelAdmin):
    list_display = ('item', 'update', 'potential')
    list_filter = ('update', 'members')
    raw_id_fields = ['item', 'update']
    search_fields = ['item__name']

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('time',)
    list_filter = ('time',)
    search_fields = ['time']

admin.site.register(Item, ItemAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Potential, PotentialAdmin)
admin.site.register(Update, UpdateAdmin)
