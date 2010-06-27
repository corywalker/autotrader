import logging
import time
import pickle
import os.path

from backend.index import loop_and_parse_indexes
from backend.detail import loop_details, get_detail_info_from_id
from backend.volume import loop_and_parse_volumes, loop_and_parse_front_volumes
from backend.analyze import compute_potentials
from backend.models import Update

LOG_FILENAME = 'autotrader.log'
ITEM_INFO_FILENAME = 'test_item_info.dat'
TEST_ITEMS = [560, 561, 562, 563]

def initialize_logging():
    logging.basicConfig(filename=LOG_FILENAME,
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    # define a Handler which writes to the sys.stderr
    console = logging.StreamHandler()
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', '%m-%d %H:%M')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

def update_items():
    loop_and_parse_indexes()
    loop_and_parse_volumes()
    loop_and_parse_front_volumes()
    loop_details()
    compute_potentials()

def get_test_item_info(delay):
    test_item_info = []
    for test_item in TEST_ITEMS:
        info = get_detail_info_from_id(test_item)
        test_item_info.append(info)
        time.sleep(delay)
    return test_item_info

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
    logging.debug('refresh() loop started.')
    test_item_info = load_item_info()
    while True:
        new_test_item_info = get_test_item_info(30)
        if new_test_item_info != test_item_info:
            logging.debug('Detected a price change:')
            logging.debug(new_test_item_info)
            logging.debug(test_item_info)
            test_item_info = new_test_item_info
            save_item_info(test_item_info)
            Update().save()
            time.sleep(600)
            update_items()
        else:
            logging.debug('No price change.')
        # Sleep for 10 minutes
        time.sleep(600)

