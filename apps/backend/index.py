import re
import logging

from BeautifulSoup import BeautifulSoup

from backend.models import Item
from backend.helper import rs_str_to_int, read_url, get_or_create_price, get_day_id

def get_index_url(letter, page):
    return 'http://services.runescape.com/m=itemdb_rs/results.ws?query=&sup=Initial%%20Letter&cat=%s&sub=All&page=%i&vis=1&order=1&sortby=name&price=&members=' % (letter, page)

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
        price = get_or_create_price(item, get_day_id())
        price.price = raw_item[3]
        price.save()

def loop_and_parse_indexes():
    letters = list('abcdefghijklmnopqrstuvwxyz')
    letters.append('Other')
    for letter in letters:
        page = 1
        while True:
            content = read_url(get_index_url(letter, page))
            if 'did not return' in content: break
            logging.debug("Parsing page %i of letter '%s'" % (page, letter))
            parse_index(content)
            if 'Next &gt;<br>' in content: break
            page += 1

