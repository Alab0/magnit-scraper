import os
import sys

sys.path.append(f'{os.getcwd()}/magnit_scraper')

import pytest
import asyncpg
from unittest.mock import AsyncMock, MagicMock, patch
from database import fetch_ids_by_table, insert_products_and_stores
from models import Product, StoreProduct


@pytest.mark.asyncio
async def test_fetch_ids_by_table_success():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [[1], [2], [3]]
    
    with patch("asyncpg.connect", return_value=mock_conn):
        result = await fetch_ids_by_table("test_table")
    
    assert result == [1, 2, 3]
    mock_conn.fetch.assert_called_once_with("SELECT id FROM test_table")
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_ids_by_table_connection_error():
    mock_conn = AsyncMock()
    mock_conn.fetch.side_effect = asyncpg.exceptions.InterfaceError("Connection failed")
    
    with patch("asyncpg.connect", return_value=mock_conn):
        result = await fetch_ids_by_table("test_table")
    
    assert result == []
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_ids_by_table_query_error():
    mock_conn = AsyncMock()
    mock_conn.fetch.side_effect = asyncpg.exceptions.PostgresError("Query failed")
    
    with patch("asyncpg.connect", return_value=mock_conn):
        result = await fetch_ids_by_table("test_table")
    
    assert result == []
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_products_and_stores_success():
    mock_conn = AsyncMock()
    
    mock_conn.transaction = MagicMock()
    mock_conn.transaction.return_value.__aenter__.return_value = mock_conn
    mock_conn.transaction.return_value.__aexit__.return_value = None

    mock_conn.executemany = AsyncMock()
    mock_conn.close = AsyncMock()

    products = [
        Product(
            id = 1, name = "Product1", price = 10000, category_id = 10, 
            store_id = 11, seo_code = "p1", brand = "Brand1", manufacturer = "Man1"
        ),
        Product(
            id = 2, name = "Product2", price = 20000, category_id = 20, 
            store_id = 21, seo_code = "p2", brand = "Brand2", manufacturer = "Man2"
        ),
    ]

    store_products = [
        StoreProduct(store_id=1, product_id=1),
        StoreProduct(store_id=2, product_id=2),
    ]

    with patch("asyncpg.connect", return_value=mock_conn):
        await insert_products_and_stores(products, store_products)

    # Проверяем, что executemany был вызван
    assert mock_conn.executemany.call_count > 0

    mock_conn.executemany.assert_any_call(
        """
        INSERT INTO product (id, name, price, seo_code, brand, manufacturer, category_id) 
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE 
        SET 
            name = EXCLUDED.name, 
            price = EXCLUDED.price,
            seo_code = EXCLUDED.seo_code,
            brand = EXCLUDED.brand,
            manufacturer = EXCLUDED.manufacturer,
            category_id = EXCLUDED.category_id;
        """,
        [(1, "Product1", 100.0, "p1", "Brand1", "Man1", 10),
         (2, "Product2", 200.0, "p2", "Brand2", "Man2", 20)]
    )
    mock_conn.executemany.assert_any_call(
        """
        INSERT INTO store_product (store_id, product_id) 
        VALUES ($1, $2)
        """,
        [(1, 1), (2, 2)]
    )

    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_products_and_stores_connection_error():
    mock_conn = AsyncMock()
    
    mock_conn.transaction = MagicMock()
    mock_conn.transaction.return_value.__aenter__.return_value = mock_conn
    mock_conn.transaction.return_value.__aexit__.return_value = None

    mock_conn.executemany.side_effect = asyncpg.exceptions.InterfaceError("Connection failed")

    with patch("asyncpg.connect", return_value=mock_conn):
        await insert_products_and_stores([], [])

    mock_conn.close.assert_awaited_once()
    

@pytest.mark.asyncio
async def test_insert_products_and_stores_query_error():
    mock_conn = AsyncMock()
    
    mock_conn.transaction = MagicMock()
    mock_conn.transaction.return_value.__aenter__.return_value = mock_conn
    mock_conn.transaction.return_value.__aexit__.return_value = None

    mock_conn.executemany.side_effect = asyncpg.exceptions.PostgresError("Query failed")

    with patch("asyncpg.connect", return_value=mock_conn):
        await insert_products_and_stores([], [])

    mock_conn.close.assert_awaited_once()