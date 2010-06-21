import re

from BeautifulSoup import BeautifulSoup

from backend.models import Item
from backend.helper import rs_str_to_int, read_url, get_or_create_price, get_day_id

def get_detail_url(rs_id):
    '''Get the item's page in the Grand Exchange database.'''
    return 'http://services.runescape.com/m=itemdb_rs/viewitem.ws?obj=%i' % rs_id

def get_detail_info(html):
    item_additional = re.search(r'<div id="item_additional"(.+)</div>', html, re.DOTALL).group(0)
    soup = BeautifulSoup(item_additional)
    item_additional = soup.find(id='item_additional')
    examine = soup.contents[0].contents[2][1:-1]
    spans = soup.findAll('span')
    min_price = int(rs_str_to_int(spans[0].contents[2][1:-1]))
    price = int(rs_str_to_int(spans[1].contents[2][1:-1]))
    max_price = int(rs_str_to_int(spans[2].contents[2][1:-1]))
    return min_price, price, max_price, examine

def parse_detail(item):
    html = read_url(get_detail_url(item.rs_id))
    info = get_detail_info(html)
    item.examine = info[3]
    item.save()
    price = get_or_create_price(item, get_day_id())
    price.min_price = info[0]
    price.price = info[1]
    price.max_price = info[2]
    price.save()

def loop_details():
    for item in Item.objects.filter(examine=None).all():
        print 'Updating the info for ID #%i' % item.rs_id
        parse_detail(item)

