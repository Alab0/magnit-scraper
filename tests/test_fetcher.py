import os
import sys

sys.path.append(f'{os.getcwd()}/magnit_scraper')

import pytest
import aiohttp
import asyncio
from aioresponses import aioresponses
from fetcher import send_post, send_get_bs4
from models import Product, RequestStatus, DetailedRequestStatus


@pytest.mark.asyncio
async def test_send_post_success():
     async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        products = asyncio.Queue()
        statuses = asyncio.Queue()
        category_id = 123
        store_id = 12

        response_data = {
            "items": [
                {"id": 1, "name": "Test Product 1", "price": 99.99, "seoCode": "Test seo_code 1"},
                {"id": 2, "name": "Test Product 2", "price": 199.99, "seoCode": "Test seo_code 2"}
            ]
        }

        with aioresponses() as mock_response:
            mock_response.post(
                f"https://magnit.ru/webgate/v2/goods/search",
                payload = response_data,
                status = 200
            )

            await send_post(session, semaphore, category_id, store_id, products, statuses)

            product = await products.get()
            request_status = await statuses.get()

            assert product.id == 1
            assert product.name == "Test Product 1"
            assert product.price == 99.99
            assert product.seo_code == "Test seo_code 1"
            assert request_status == 200


@pytest.mark.asyncio
async def test_fetch_product_client_error():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        products = asyncio.Queue()
        statuses = asyncio.Queue()
        category_id = 123
        store_id = 12

        with aioresponses() as mock_response:
            mock_response.post(
                "https://magnit.ru/webgate/v2/goods/search",
                status=404
            )

            await send_post(session, semaphore, category_id, store_id, products, statuses)

            assert products.empty()
            request_status = await statuses.get()

            assert isinstance(request_status, DetailedRequestStatus)

            assert request_status.status == "404"
            assert request_status.url == "https://magnit.ru/webgate/v2/goods/search"
            assert request_status.category_id == category_id
            assert request_status.store_id == store_id
            assert request_status.offset == 0


@pytest.mark.asyncio
async def test_fetch_product_server_error():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        products = asyncio.Queue()
        statuses = asyncio.Queue()
        category_id = 123
        store_id = 12

        with aioresponses() as mock_response:
            for _ in range(3):
                mock_response.post(
                    "https://magnit.ru/webgate/v2/goods/search",
                    status=503
                )

            await send_post(session, semaphore, category_id, store_id, products, statuses)

            assert products.empty()
            request_status = await statuses.get()

            assert isinstance(request_status, DetailedRequestStatus)

            assert request_status.status == "503"
            assert request_status.url == "https://magnit.ru/webgate/v2/goods/search"
            assert request_status.category_id == category_id
            assert request_status.store_id == store_id
            assert request_status.offset == 0


@pytest.mark.asyncio
async def test_fetch_product_timeout():
   async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        products = asyncio.Queue()
        statuses = asyncio.Queue()
        category_id = 123
        store_id = 12

        with aioresponses() as mock_response:
            for _ in range(3):
                mock_response.post(
                    "https://magnit.ru/webgate/v2/goods/search",
                    exception=asyncio.TimeoutError
                )

            await send_post(session, semaphore, category_id, store_id, products, statuses)

            assert products.empty()
            request_status = await statuses.get()

            assert isinstance(request_status, DetailedRequestStatus)

            assert request_status.status == "Timeout error"
            assert request_status.url == "https://magnit.ru/webgate/v2/goods/search"
            assert request_status.category_id == category_id
            assert request_status.store_id == store_id
            assert request_status.offset == 0


@pytest.mark.asyncio
async def test_fetch_product_exception():
   async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        products = asyncio.Queue()
        statuses = asyncio.Queue()
        category_id = 123
        store_id = 12

        with aioresponses() as mock_response:
            for _ in range(3):
                mock_response.post(
                    "https://magnit.ru/webgate/v2/goods/search",
                    exception=Exception("Unexpected Error")
                )

            await send_post(session, semaphore, category_id, store_id, products, statuses)

            assert products.empty()
            request_status = await statuses.get()

            assert isinstance(request_status, DetailedRequestStatus)

            assert request_status.status == "Unexpected Error"
            assert request_status.url == "https://magnit.ru/webgate/v2/goods/search"
            assert request_status.category_id == category_id
            assert request_status.store_id == store_id
            assert request_status.offset == 0


@pytest.mark.asyncio
async def test_send_get_bs4_success():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        statuses = asyncio.Queue()

        product = Product(1, "Test Product 1", 99.99, 123, 12, "test-seo-code-1")
        body = '''
            <span itemprop="brand">Test Brand</span>
            <span itemprop="manufacturer">Test Manufacturer</span>
        '''
        
        with aioresponses() as mock_response:
            mock_response.get(
                f"https://magnit.ru/product/{product.id}-{product.seo_code}",
                body = body,
                status = 200
            )

            await send_get_bs4(session, semaphore, product, statuses)

            request_status = await statuses.get()

            assert product.brand == "Test Brand"
            assert product.manufacturer == "Test Manufacturer"
            assert request_status == 200


@pytest.mark.asyncio
async def test_send_get_bs4_client_error():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        statuses = asyncio.Queue()

        product = Product(1, "Test Product 1", 99.99, 123, 12, "test-seo-code-1")
        
        with aioresponses() as mock_response:
            mock_response.get(
                f"https://magnit.ru/product/{product.id}-{product.seo_code}",
                status = 404
            )

            await send_get_bs4(session, semaphore, product, statuses)

            request_status = await statuses.get()
            assert isinstance(request_status, RequestStatus)

            assert product.brand == None
            assert product.manufacturer == None
            assert request_status.status == "404"
            assert request_status.url == f"https://magnit.ru/product/{product.id}-{product.seo_code}"


@pytest.mark.asyncio
async def test_send_get_bs4_server_error():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        statuses = asyncio.Queue()

        product = Product(1, "Test Product 1", 99.99, 123, 12, "test-seo-code-1")
        
        with aioresponses() as mock_response:
            for _ in range(3):
                mock_response.get(
                    f"https://magnit.ru/product/{product.id}-{product.seo_code}",
                    status = 503
                )

            await send_get_bs4(session, semaphore, product, statuses)

            request_status = await statuses.get()
            assert isinstance(request_status, RequestStatus)

            assert product.brand == None
            assert product.manufacturer == None
            assert request_status.status == "503"
            assert request_status.url == f"https://magnit.ru/product/{product.id}-{product.seo_code}"


@pytest.mark.asyncio
async def test_send_get_bs4_timeout():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        statuses = asyncio.Queue()

        product = Product(1, "Test Product 1", 99.99, 123, 12, "test-seo-code-1")
        
        with aioresponses() as mock_response:
            for _ in range(3):
                mock_response.get(
                    f"https://magnit.ru/product/{product.id}-{product.seo_code}",
                    exception=asyncio.TimeoutError
                )

            await send_get_bs4(session, semaphore, product, statuses)

            request_status = await statuses.get()
            assert isinstance(request_status, RequestStatus)

            assert product.brand == None
            assert product.manufacturer == None
            assert request_status.status == "Timeout error"
            assert request_status.url == f"https://magnit.ru/product/{product.id}-{product.seo_code}"


@pytest.mark.asyncio
async def test_send_get_bs4_exception():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        statuses = asyncio.Queue()

        product = Product(1, "Test Product 1", 99.99, 123, 12, "test-seo-code-1")
        
        with aioresponses() as mock_response:
            for _ in range(3):
                mock_response.get(
                    f"https://magnit.ru/product/{product.id}-{product.seo_code}",
                    exception=Exception("Unexpected Error")
                )

            await send_get_bs4(session, semaphore, product, statuses)

            request_status = await statuses.get()
            assert isinstance(request_status, RequestStatus)

            assert product.brand == None
            assert product.manufacturer == None
            assert request_status.status == "Unexpected Error"
            assert request_status.url == f"https://magnit.ru/product/{product.id}-{product.seo_code}"