import logging
import time
import pickle
import os.path

from backend.index import loop_and_parse_indexes
from backend.detail import loop_details
from backend.volume import loop_and_parse_volumes, loop_and_parse_front_volumes, get_front_volume_info
from backend.analyze import compute_potentials
from backend.models import Update

LOG_FILENAME = 'autotrader.log'
ITEM_INFO_FILENAME = 'test_item_info.dat'

def add_file_log(filename):
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', '%m-%d %H:%M')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)

def add_console_log():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', '%m-%d %H:%M')
    handler.setFormatter(formatter)
    handler.setLevel(5)
    logging.getLogger().addHandler(handler)

def initialize_logging():
    add_file_log(LOG_FILENAME)
    add_console_log()

def update_items():
    loop_and_parse_indexes()
    loop_and_parse_volumes()
    loop_and_parse_front_volumes()
    loop_details()
    compute_potentials()

def load_item_info():
    if not os.path.exists(ITEM_INFO_FILENAME):
        file = open(ITEM_INFO_FILENAME, 'w')
        pickle.dump([], file)
        file.close()
    file = open(ITEM_INFO_FILENAME, 'r')
    item_info = pickle.load(file)
    file.close()
    return item_info

def save_item_info(item_info):
    file = open(ITEM_INFO_FILENAME, 'w')
    pickle.dump(item_info, file)
    file.close()

def refresh():
    initialize_logging()
    logging.info('refresh() loop started.')
    test_item_info = load_item_info()
    while True:
        new_test_item_info = list(get_front_volume_info())
        if new_test_item_info != test_item_info:
            logging.info('Detected a GE update:')
            logging.debug(new_test_item_info)
            logging.debug(test_item_info)
            test_item_info = new_test_item_info
            save_item_info(test_item_info)
            Update().save()
            # Sleep for 10 minutes
            time.sleep(600)
            update_items()
        else:
            logging.debug('No GE update.')
        # Sleep for 20 minutes
        time.sleep(1200)

