import logging

from backend.models import Price, Item, Potential
from backend.statistics import average, derivative, linreg
from backend.helper import latest_update

def get_price_objects(item, days):
    return Price.objects.filter(item=item).order_by('-update__time')[:days]

def get_prices(item, days):
    price_list = []
    for price in get_price_objects(item, days):
        price_list.append(price.price)
    return price_list

def get_price_changes(item, days):
    prices = get_prices(item, days+1)
    return derivative(prices)

def get_price_change_regression(item, days):
    y = get_price_changes(item, days)
    x = range(0, len(y))
    return linreg(x, y)

def average_price(item, days):
    return average(get_prices(item, days))

def compute_potential(item):
    potential = 0
    # Get the info we need
    prices = get_prices(item, 30)
    price_objects = get_price_objects(item, 30)
    try:
        average = average_price(item, 30)
    except ZeroDivisionError:
        logging.log(5, 'Not enough price history.')
        return potential
    price_changes = get_price_changes(item, 30)
    # Calculate the potential
    try:
        regression = get_price_change_regression(item, 4)
    except ZeroDivisionError:
        logging.log(5, 'Not enough price history.')
        return potential
    dip = (1 - (prices[0] / average)) * 100
    logging.log(5, 'Dip is %f%%, adding %f.' % (dip, dip * 5))
    potential += dip * 5
    if regression[0] >= 1:
        logging.log(5, 'The change slope (%f) is at least 1. Adding 80.' % regression[0])
        potential += 80
    if price_changes[0] <= 0:
        logging.log(5, 'The latest price change (%d) was not positive. Adding 80.' % price_changes[0])
        potential += 80
    if price_objects[0].volume != None:
        logging.log(5, 'This item is frequently traded. Adding 80.')
        potential += 80
    if average >= 10:
        logging.log(5, 'This item has a decently high price. Adding 80.')
        potential += 80
    return potential

def compute_potentials():
    logging.info('Computing potentials for each item.')
    for item in Item.objects.all():
        logging.debug('Computing potential for item #%i' % item.rs_id)
        p, new = Potential.objects.get_or_create(item=item, update=latest_update())
        p.potential = compute_potential(item)
        p.members = item.members
        p.save()

