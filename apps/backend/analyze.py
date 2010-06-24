from backend.models import Price, Item
from backend.statistics import average, derivative, linreg

def get_prices(item, days):
    price_list = []
    prices = Price.objects.filter(item=item).order_by('-day')[:days]
    for price in prices:
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
    for item in Item.objects.all():
        prices = get_prices(item, 30)
        average = average_price(item, 30)
        price_changes = get_price_changes(item, 30)
        regression = get_price_change_regression(item, days)
        dip = 1 - (prices[0] / average)
