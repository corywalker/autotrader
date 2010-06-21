from backend.models import Item, Price

import urllib2
import httplib
import re
import datetime
from BeautifulSoup import BeautifulSoup

def get_index_url(letter, page):
    return 'http://services.runescape.com/m=itemdb_rs/results.ws?query=&sup=Initial%%20Letter&cat=%s&sub=All&page=%i&vis=1&order=1&sortby=name&price=&members=' % (letter, page)

def get_detail_url(rs_id):
    '''Get the item's page in the Grand Exchange database.'''
    return 'http://services.runescape.com/m=itemdb_rs/viewitem.ws?obj=%i' % rs_id

def rs_str_to_int(string):
    string = string.replace(',', '')
    if string[-1] == 'k':
        num = float(string[:-1]) * 1000
    elif string[-1] == 'm':
        num = float(string[:-1]) * 1000000
    else:
        num = float(string)
    return int(num + 0.5)

def get_index_info(html):
    table = re.search(r'<table id="search_results_table"(.+)</table>', html, re.DOTALL).group(0)
    soup = BeautifulSoup(table)
    raw_entries = soup.findAll('tr')[1:-1]
    for raw_entry in raw_entries:
        soup = BeautifulSoup(str(raw_entry))
        columns = soup.findAll('td')
        id = int(re.search(r'id=(\d+)', str(columns[0])).group(1))
        name = soup.find('img')['alt']
        price = rs_str_to_int(columns[2].contents[0])
        members = 'star_members.png' in str(columns[4])
        yield (id, name, members, price)

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

def get_day_id():
    return (datetime.date.today()-datetime.date(2010,1,1)).days

def parse_index(html):
    for raw_item in get_index_info(html):
        try:
            item = Item.objects.get(rs_id=raw_item[0])
            item.name = raw_item[1]
            item.members = raw_item[2]
            item.save()
        except Item.DoesNotExist:
            item = Item(rs_id=raw_item[0], name=raw_item[1], members=raw_item[2])
            item.save()
        day = get_day_id()
        try:
            price = Price.objects.get(item=item, day=day)
        except Price.DoesNotExist:
            price = Price(item=item, day=day)
        price.price = raw_item[3]
        price.save()

def parse_detail(item):
    html = read_url(get_detail_url(item.rs_id))
    info = get_detail_info(html)
    item.examine = info[3]
    item.save()
    day = get_day_id()
    try:
    	price = Price.objects.get(item=item, day=day)
    except Price.DoesNotExist:
        price = Price(item=item, day=day)
    price.min_price = info[0]
    price.price = info[1]
    price.max_price = info[2]
    price.save()

def read_url(url):
    success = False
    while not success:
        try:
            content = urllib2.urlopen(url).read()
            success = True
        except httplib.BadStatusLine, urllib2.URLError:
            print 'There was an error. Retrying...'
    return content

def loop_and_parse_indexes():
    letters = list('abcdefghijklmnopqrstuvwxyz')
    letters.append('Other')
    for letter in letters:
        page = 1
        while True:
            content = read_url(get_index_url(letter, page))
            if 'did not return' in content: break
            print letter, page, url
            parse_index(content)
            if 'Next &gt;<br>' in content: break
            page += 1

def loop_details():
    for item in Item.objects.filter(examine=None).all():
        print 'Updating the info for ID #%i' % item.rs_id
        parse_detail(item)

def update_items():
    loop_and_parse_indexes()

#update_items()
loop_details()
