import logging

from backend.index import loop_and_parse_indexes
from backend.detail import loop_details
from backend.volume import loop_and_parse_volumes, loop_and_parse_front_volumes

LOG_FILENAME = 'autotrader.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def update_items():
    loop_and_parse_indexes()
    loop_and_parse_volumes()
    loop_and_parse_front_volumes()
    loop_details()

update_items()
