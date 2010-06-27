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

def compute_potentials():
    logging.info('Computing potentials for each item.')
    for item in Item.objects.all():
        logging.debug('Computing potential for item #%i' % item.rs_id)
        prices = get_prices(item, 30)
        price_objects = get_price_objects(item, 30)
        average = average_price(item, 30)
        price_changes = get_price_changes(item, 30)
        p, new = Potential.objects.get_or_create(item=item, update=latest_update())
        p.potential = 0
        # Hack! Needs to just set a zero potential if fails.
        try:
            regression = get_price_change_regression(item, 4)
        except ZeroDivisionError:
  	    p.save()
            continue
        dip = 1 - (prices[0] / average)
        p.potential += dip * 5
        if regression[0] >= 1:
            p.potential += 80
        if price_changes[0] <= 0:
            p.potential += 80
        if price_objects[0].volume != None:
            p.potential += 80
        p.save()

