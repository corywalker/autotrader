import urllib2
import httplib
import datetime
import logging

from backend.models import Price, Update

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

def latest_update():
    return Update.objects.latest()

def get_or_create_price(item, update):
    try:
        price = Price.objects.get(item=item, update=update)
    except Price.DoesNotExist:
        price = Price(item=item, update=update)
    return price

def read_url(url):
    success = False
    while not success:
        try:
            content = urllib2.urlopen(url).read()
            success = True
        except (httplib.BadStatusLine, urllib2.URLError):
            logging.debug('There was an error. Retrying %s' % url)
    return content

