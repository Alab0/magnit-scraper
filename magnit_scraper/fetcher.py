import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import py_logger
from models import Product, RequestStatus, DetailedRequestStatus
from utils import generate_headers, generate_post_data


async def send_post(
    session: aiohttp.ClientSession, 
    semaphore: asyncio.Semaphore, 
    category_id: int, 
    store_id: int, 
    store_products: asyncio.Queue, 
    statuses: asyncio.Queue
):
    async with semaphore: 
        URL = "https://magnit.ru/webgate/v2/goods/search"
        offset = 0
        status_failed_request = 0

        # Цикл для получения всех страниц в категории
        while True:
            # Цикл нескольких попыток в случае неудачного запроса
            for attempt in range(3):
                try:
                    data = generate_post_data(offset, category_id, store_id)
                    headers = generate_headers(store_id)
                    async with session.post(URL, headers=headers, json=data) as response:
                        py_logger.info(f"Category id: {category_id}, Store id: {store_id}, Offset: {offset}, Status: {response.status}")

                        if response.status == 200:
                            await statuses.put(response.status)
                            response_json = await response.json()
                            items = response_json.get('items', [])

                            for item in items:
                                await store_products.put(
                                    Product(
                                        item["id"], item["name"], item["price"], category_id, store_id, seo_code=item["seoCode"]
                                    )
                                )

                            #Проверка послендней страницы
                            if len(items) < 50:
                                return
                            offset += 50
                            break # Выходим из цикла нескольких попыток
                        elif response.status in range(500, 511):
                            status_failed_request = response.status
                        else:
                            await statuses.put(DetailedRequestStatus(str(response.status), URL, category_id, store_id, offset))
                            return # Выходим из цикла получения всех страниц в категории

                except asyncio.TimeoutError:
                    py_logger.info(f"Timeout error fetching. Category_id {category_id}, Store_id {store_id}, Offset: {offset}")
                    status_failed_request = "Timeout error"

                except Exception as e:
                    py_logger.exception(f"Unexpected error fetching. Category_id {category_id}, Store_id {store_id}, Offset {offset}: {e}")
                    await statuses.put(DetailedRequestStatus(str(e), URL, category_id, store_id, offset))
                    return # Выходим из цикла получения всех страниц в категории

                # Задрежка 5xx или TimeoutError
                wait_time = attempt * 10
                py_logger.info(f"Retrying in {wait_time:.2f} sec...")
                await asyncio.sleep(wait_time)

            else:
                py_logger.info(f"Failed to get fetching. Category_id {category_id}, "
                               f"Store_id {store_id}, Offset: {offset}, Status: {status_failed_request}")
                await statuses.put(DetailedRequestStatus(str(status_failed_request), URL, category_id, store_id, offset))
                break # Выходим из цикла получения всех страниц в категории


async def fetch_products(
    store_products: asyncio.Queue, 
    statuses: asyncio.Queue, 
    categories: list, 
    stores: list
):
    semaphore = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as session:
        tasks = [
            send_post(session, semaphore, category_id, store_id, store_products, statuses) 
            for category_id in categories
            for store_id in stores
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        
    
async def send_get_bs4(
    session: aiohttp.ClientSession, 
    semaphore: asyncio.Semaphore, 
    product: Product, 
    statuses: asyncio.Queue
):
    async with semaphore:

        URL = f"https://magnit.ru/product/{product.id}-{product.seo_code}"
        status_failed_request = 0

        # Цикл нескольких попыток в случае неудачного запроса
        for attempt in range(3):
            try:
                async with session.get(URL, headers=generate_headers(product.store_id), timeout=10) as response:
                    py_logger.info(f"Product id: {product.id}, Store id: {product.store_id}, Status: {response.status}")

                    if response.status == 200:
                        await statuses.put(response.status)
                        soup = BeautifulSoup(await response.text(), "html.parser")
                        brand = soup.find(attrs={"itemprop": "brand"})
                        manufacturer = soup.find(attrs={"itemprop": "manufacturer"})
                        if brand: product.brand = brand.text.strip()
                        if manufacturer: product.manufacturer = manufacturer.text.strip()
                        return # Выходим из функции
                    elif response.status in range(500, 511):
                        status_failed_request = response.status
                    else:
                        await statuses.put(RequestStatus(str(response.status), URL))
                        return  # Выходим из функции

            except asyncio.TimeoutError:
                py_logger.info(f"Timeout error details. URL: {URL}")
                status_failed_request = "Timeout error"

            except Exception as e:
                py_logger.exception(f"Unexpected error details. URL: {URL}, Exception: {e}")
                await statuses.put(RequestStatus(str(e), URL))
                return # Выходим из функции

            # Задрежка 5xx или TimeoutError
            wait_time = attempt * 10
            py_logger.info(f"Retrying in {wait_time:.2f} sec...")
            await asyncio.sleep(wait_time)

        else:
            py_logger.info(f"Failed to get details. URL: {URL}, Status: {status_failed_request}")
            await statuses.put(RequestStatus(str(status_failed_request), URL))
            

async def fetch_product_details(products: asyncio.Queue, statuses: asyncio.Queue):
    semaphore = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as session:
        tasks = []
        container_queue = asyncio.Queue()

        while not products.empty():
            product = await products.get()
            await container_queue.put(product)
            tasks.append(send_get_bs4(session, semaphore, product, statuses))

        while not container_queue.empty():
            await products.put(await container_queue.get())

        await asyncio.gather(*tasks, return_exceptions=True)