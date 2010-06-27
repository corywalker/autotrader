import re
import logging

from BeautifulSoup import BeautifulSoup

from backend.models import Item, Price
from backend.helper import rs_str_to_int, read_url, get_or_create_price, latest_update

FRONT_VOLUME_URL = 'http://services.runescape.com/m=itemdb_rs/frontpage.ws?listview=1'
VOLUME_URL = 'http://services.runescape.com/m=itemdb_rs/top100.ws?list=0&scale=0'

def get_volume_info():
    html = read_url(VOLUME_URL)
    table = re.search(r'<table id="top100_table"(.+)</table>', html, re.DOTALL).group(0)
    soup = BeautifulSoup(table)
    raw_entries = soup.findAll('tr')[1:]
    for raw_entry in raw_entries:
        soup = BeautifulSoup(str(raw_entry))
        columns = soup.findAll('td')
        id = int(re.search(r'id=(\d+)', str(columns[0])).group(1))
        volume = rs_str_to_int(columns[5].contents[0])
        yield id, volume

def get_front_volume_info():
    html = read_url(FRONT_VOLUME_URL)
    top5_left = re.search(r'<div class="top5_left(.+)', html, re.DOTALL).group(0)
    soup = BeautifulSoup(top5_left)
    table = soup.find('table')
    raw_entries = table.findAll('tr')[1:]
    for raw_entry in raw_entries:
        soup = BeautifulSoup(str(raw_entry))
        columns = soup.findAll('td')
        id = int(re.search(r'id=(\d+)', str(columns[0])).group(1))
        volume = rs_str_to_int(columns[3].contents[0][:-1])
        yield id, volume

def loop_and_parse_volumes():
    logging.info('Updating 7-day volume info.')
    for info in get_volume_info():
        item = Item.objects.get(rs_id=info[0])
        try:
            price = Price.objects.get(item=item, update=latest_update())
            logging.debug('Updating the info for ID #%i' % item.rs_id)
            price.seven_day_volume = info[1]
            price.save()
        except Price.DoesNotExist: pass

def loop_and_parse_front_volumes():
    logging.info('Updating volume info.')
    for info in get_front_volume_info():
        item = Item.objects.get(rs_id=info[0])
        try:
            price = Price.objects.get(item=item, update=latest_update())
            logging.debug('Updating the info for ID #%i' % item.rs_id)
            price.volume = info[1]
            price.save()
        except Price.DoesNotExist: pass

