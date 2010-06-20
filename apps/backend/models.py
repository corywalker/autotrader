from django.db import models

class Item(models.Model):
    '''An item linked to an item in RS.'''
    rs_id = models.PositiveIntegerField(verbose_name='Runescape ID')
    name = models.CharField(max_length=10)
    members = models.BooleanField()
    examine = models.CharField(max_length=150, blank=True, null=True)

    def get_url():
        '''Get the item's page in the Grand Exchange database.'''
        return 'http://services.runescape.com/m=itemdb_rs/viewitem.ws?obj=%i' % rs_id

    def get_sprite():
        '''Get the sprite image of the item.'''
        return 'http://services.runescape.com/m=itemdb_rs/3032_obj_sprite.gif?id=%i' % rs_id

    def get_picture():
        '''Get the 3D rendering of the item.'''
        return 'http://services.runescape.com/m=itemdb_rs/3032_obj_big.gif?id=%i' % rs_id

    def get_graph(scale):
        '''Get the latest graph of the item.

        scale is 0 for 30 days, 1 for 90 days, and 2 for 180 days.
        '''
        return 'http://services.runescape.com/m=itemdb_rs/3032_graphimg3.gif?id=%i&scale=%i' % (rs_id, scale)

    def get_axis(scale, axis):
        '''Get the latest graph of the item.

        scale is 0 for 30 days, 1 for 90 days, and 2 for 180 days.
        axis is 0 for y and 2 for x
        '''
        return 'http://services.runescape.com/m=itemdb_rs/3032_scaleimg3.gif?id=%i&scale=%i&axis=%i' % (rs_id, scale, axis)


class Price(models.Model):
    '''A price of an Item on any given day.'''
    item = models.ForeignKey(Item)
    day = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    max_price = models.PositiveIntegerField()
    min_price = models.PositiveIntegerField()
    volume = models.PositiveIntegerField(blank=True, null=True)
    seven_day_volume = models.PositiveIntegerField(blank=True, null=True)

