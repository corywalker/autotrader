from backend.models import Item, Price

import urllib2
import httplib
import re
from BeautifulSoup import BeautifulSoup

def get_index_url(letter, page):
    return 'http://services.runescape.com/m=itemdb_rs/results.ws?query=&sup=Initial%%20Letter&cat=%s&sub=All&page=%i&vis=1&order=1&sortby=name&price=&members=' % (letter, page)

def rs_str_to_int(string):
    string = string.replace(',', '')
    if string[-1] == 'k':
        num = float(string[:-1]) * 1000
    elif string[-1] == 'm':
        num = float(string[:-1]) * 1000000
    else:
        num = float(string)
    return int(num + 0.5)

def get_page_results(html):
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

def parse_page(html):
    for raw_item in get_page_results(html):
        try:
            item = Item.objects.get(rs_id=raw_item[0])
            item.name = raw_item[1]
            item.members = raw_item[2]
            item.save()
        except Item.DoesNotExist:
            Item(rs_id=raw_item[0], name=raw_item[1], members=raw_item[2]).save()

def update_items():
    letters = list('abcdefghijklmnopqrstuvwxyz')
    letters.append('Other')
    for letter in letters:
        page = 1
        while True:
            url = get_index_url(letter, page)
            success = False
            while not success:
                try:
                    content = urllib2.urlopen(url).read()
                    success = True
                except httplib.BadStatusLine, urllib2.URLError:
                    print 'There was an error. Retrying...'
            if 'did not return' in content: break
            print letter, page, url
            parse_page(content)
            if 'Next &gt;<br>' in content: break
            page += 1

update_items()
