import logging
import time
import pickle
import os.path

from backend.index import loop_and_parse_indexes
from backend.detail import loop_details, get_detail_info_from_id
from backend.volume import loop_and_parse_volumes, loop_and_parse_front_volumes

LOG_FILENAME = 'autotrader.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
ITEM_INFO_FILENAME = 'test_item_info.dat'
TEST_ITEMS = [560, 561, 562, 563]

def update_items():
    loop_and_parse_indexes()
    loop_and_parse_volumes()
    loop_and_parse_front_volumes()
    loop_details()

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

def wait_for_update():
    test_item_info = load_item_info()
    while True:
        new_test_item_info = get_test_item_info(30)
        if new_test_item_info != test_item_info:
            logging.debug(new_test_item_info)
            logging.debug(test_item_info)
            test_item_info = new_test_item_info
            save_item_info(test_item_info)
            time.sleep(300)
            update_items()
        # Sleep for 5 minutes
        time.sleep(300)

