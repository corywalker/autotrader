import logging

from backend.refresh import add_console_log
from backend.analyze import compute_potential
from backend.models import Item

logging.getLogger().setLevel(0)
add_console_log()

item_name = raw_input('What is the name of the item? ')
item = Item.objects.get(name=item_name)
print compute_potential(item)
