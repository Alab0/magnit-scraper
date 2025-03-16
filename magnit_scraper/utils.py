import os
import asyncio
from collections import Counter
from models import Product, RequestStatus, DetailedRequestStatus
from config import py_logger, HEADERS_TEMPLATE, POST_DATA_TEMPLATE

current_path = os.path.abspath(__file__)
parent_path = os.path.dirname(current_path)
grandparent_path = os.path.dirname(parent_path)


def generate_headers(store_id):
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] += f"; shopCode={store_id}"
    return headers


def generate_post_data(offset, category, store):
    post_data = POST_DATA_TEMPLATE.copy()
    post_data["pagination"]["offset"] = offset
    post_data["categories"] = [category]
    post_data["storeCode"] = f"{store}"
    return post_data


def write_file(lst: list, name_file: str):
    try:    
        with open(f"{grandparent_path}/failed_records/{name_file}.txt", "w", encoding="utf-8") as f:
            for item in lst:
                if type(item) == Product:
                    f.write(
                        f"{item.id};{item.name};{item.price};{item.category_id};"
                        f"{item.store_id};{item.brand};{item.manufacturer}\n"
                    )
                else:
                    f.write(f"{item.store_id};{item.product_id}\n")
    except IOError as e:
        py_logger.exception(f"Error writing to file: {e}")


def log_status(statuses: list):
    status_counts = Counter(statuses)
    for item, count in status_counts.items():
        match item:
            case int(value):
                py_logger.info(f"Status {value}: {count}")
            case DetailedRequestStatus(status, url, category_id, store_id, offset):
                py_logger.info(
                    f"Failed post request. Status: {status}, URL: {url}, "
                    f"Category id: {category_id}, Store id: {store_id}, Offset: {offset}"
                )
            case RequestStatus(status, url):
                py_logger.info(f"Failed request bs4. Status: {status}, URL: {url}")


async def queue_to_list(queue: asyncio.Queue) -> list:
    lst = []
    while True:
        try:
            lst.append(queue.get_nowait())
        except asyncio.QueueEmpty:
            break
    return lst


async def list_to_queue(lst: list) -> asyncio.Queue:
    queue = asyncio.Queue()
    for item in lst:
        queue.put_nowait(item)
    return queue


def dell_duplicates(lst: list, name_list: str) -> list:
    new_lst = list(set(lst))
    py_logger.info(f'{name_list}: {len(new_lst)}')
    return new_lst