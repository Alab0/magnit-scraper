import asyncio
import time
from config import py_logger
from models import StoreProduct
from database import fetch_ids_by_table, insert_products_and_stores
from utils import log_status, queue_to_list, dell_duplicates, list_to_queue
from fetcher import fetch_products, fetch_product_details


async def main():
    start_time = time.perf_counter()

    categories = await fetch_ids_by_table("category")
    stores = await fetch_ids_by_table("store")

    if not categories or not stores:
        return
    
    # Сбор товаров из категорий
    products_queue = asyncio.Queue()
    statuses_queue = asyncio.Queue()
    await fetch_products(products_queue, statuses_queue, categories, stores)
    py_logger.info(f"Execution time fetch products: {time.perf_counter() - start_time:.2f} seconds")
    start_time = time.perf_counter()
    log_status(await queue_to_list(statuses_queue))

    if products_queue.empty():
        return

    # Сбор деталей о товарах
    products = await queue_to_list(products_queue)
    store_products = dell_duplicates(
        [StoreProduct(p.store_id, p.id) for p in products], 
        "StoreProducts"
    )
    products_queue = await list_to_queue(
        dell_duplicates(products, "Products")
    )
    await fetch_product_details(products_queue, statuses_queue)
    products = await queue_to_list(products_queue)
    py_logger.info(f"Execution time fetch product details: {time.perf_counter() - start_time:.2f} seconds")
    start_time = time.perf_counter()
    log_status(await queue_to_list(statuses_queue))
    
    # Запись в базу данных
    await insert_products_and_stores(products, store_products)
    py_logger.info(f"Execution time insert products and stores: {time.perf_counter() - start_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())