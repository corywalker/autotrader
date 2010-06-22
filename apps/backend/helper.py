import urllib2
import httplib
import datetime

from backend.models import Price

def rs_str_to_int(string):
    string = string.replace(',', '')
    if string[-1] == 'k':
        num = float(string[:-1]) * 1000
    elif string[-1] == 'm':
        num = float(string[:-1]) * 1000000
    elif string[-1] == 'b':
        num = float(string[:-1]) * 1000000000
    else:
        num = float(string)
    return int(num + 0.5)

def get_day_id():
    return (datetime.date.today()-datetime.date(2010,1,1)).days

def get_or_create_price(item, day):
    try:
        price = Price.objects.get(item=item, day=day)
    except Price.DoesNotExist:
        price = Price(item=item, day=day)
    return price

def read_url(url):
    success = False
    while not success:
        try:
            content = urllib2.urlopen(url).read()
            success = True
        except httplib.BadStatusLine, urllib2.URLError:
            print 'There was an error. Retrying...'
    return content

