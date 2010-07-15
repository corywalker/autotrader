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
    # Perform some ordering gymnastics to get it in positive time and
    # have the latest change at x=0
    y = get_price_changes(item, days)
    y.reverse()
    x = range(-len(y) + 1, 1)
    #logging.log(5, str(x))
    #logging.log(5, str(y))
    return linreg(x, y)

def get_price_change_percents(item, days):
    prices = get_prices(item, days+1)
    percents = []
    for i in range(1, len(prices)):
        change = prices[i-1] - prices[i]
        percent = (float(change) / float(prices[i])) * 100
        percents.append(percent)
    return percents

def is_manipulated(item):
    percents = get_price_change_percents(item, 5)
    count = 0
    for percent in percents:
        if abs(percent) > 4:
            count += 1
    return count >= 4

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
        regression = get_price_change_regression(item, 3)
    except ZeroDivisionError:
        logging.log(5, 'Not enough price history.')
        return potential
    logging.log(5, 'The price data is %s.' % (prices[:5],))
    logging.log(5, 'Average price over 30 days is %f' % average)
    logging.log(5, 'The price change data is %s.' % (price_changes[:5],))
    logging.log(5, 'The price change regression data is %s.' % (regression,))
    dip = (1 - (prices[0] / average)) * 100
    logging.log(5, 'Dip is %f%%, adding %f.' % (dip, min(dip * 10, 150)))
    potential += min(dip * 10, 150)
    if regression[0] > 0:
        logging.log(5, 'The change slope (%f) is positive. Adding 80.' % regression[0])
        potential += 80
    if price_changes[0] <= 0:
        logging.log(5, 'The latest price change (%d) was negative. Adding 80.' % price_changes[0])
        potential += 80
        price_change_percent = -price_changes[0] / average * 100
        if price_change_percent < 2.0:
            logging.log(5, 'The latest price change percent (%f) is less than 2.0. Adding 80.' % price_change_percent)
            potential += 80
    if price_objects[0].volume != None:
        logging.log(5, 'This item is frequently traded. Adding 100.')
        potential += 100
    if average >= 10:
        logging.log(5, 'This item has a decently high price. Adding 80.')
        potential += 80
    if is_manipulated(item):
        logging.log(5, 'This item has possibly been manipulated by a clan. Subtracting 100.')
        potential -= 100
    return potential

def compute_potentials():
    logging.info('Computing potentials for each item.')
    for item in Item.objects.all():
        logging.debug('Computing potential for item #%i' % item.rs_id)
        p, new = Potential.objects.get_or_create(item=item, update=latest_update())
        p.potential = compute_potential(item)
        p.members = item.members
        p.save()

