from backend.index import loop_and_parse_indexes
from backend.detail import loop_details
from backend.volume import loop_and_parse_volumes, loop_and_parse_front_volumes

def update_items():
    loop_and_parse_indexes()
    loop_details()
    loop_and_parse_volumes()
    loop_and_parse_front_volumes()

update_items()
