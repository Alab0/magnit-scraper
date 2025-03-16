import asyncpg
from config import py_logger, DB_CONFIG
from utils import write_file


def handle_exception(products, store_products, message):
    py_logger.exception(f"{message}")
    write_file(products, "products")
    write_file(store_products, "store_products")


async def insert_products_and_stores(products: list, store_products: list):
    conn = None
    
    try:
        conn = await asyncpg.connect(**DB_CONFIG)

        data = [(int(p.id), p.name, p.price / 100, p.seo_code, p.brand, p.manufacturer, p.category_id) for p in products]
        sql = """
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
        """
        async with conn.transaction():
            await conn.executemany(sql, data)
            py_logger.info(f"Inserting into the database {len(data)} products")

        data = [(int(p.store_id), int(p.product_id)) for p in store_products]
        sql = """
        INSERT INTO store_product (store_id, product_id) 
        VALUES ($1, $2)
        """
        async with conn.transaction():
            await conn.executemany(sql, data)
            py_logger.info(f"Inserting into the database {len(data)} store_products")
            
    except asyncpg.exceptions.InterfaceError as e:
        handle_exception(products, store_products, f"Error connecting to database: {e}")
    except asyncpg.exceptions.PostgresError as e:
        handle_exception(products, store_products, f"Error executing SQL query: {e}")
    except Exception as e:
        handle_exception(products, store_products, f"Unexpected error: {e}")
    finally:
        if conn:
            await conn.close()


async def fetch_ids_by_table(table_name: str) -> list:
    rows = []
    conn = None

    try:
        conn = await asyncpg.connect(**DB_CONFIG)

        query = f"SELECT id FROM {table_name}"
        if table_name == "category":
            query += " WHERE is_final=true"
        rows = await conn.fetch(query)

    except asyncpg.exceptions.InterfaceError as e:
        py_logger.exception(f"Error connecting to database: {e}")
    except asyncpg.exceptions.PostgresError as e:
        py_logger.exception(f"Error executing SQL query: {e}")
    except Exception as e:
        py_logger.exception(f"Unexpected error: {e}")
    finally:
        if conn:
            await conn.close()

    return [row[0] for row in rows]