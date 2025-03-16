import os
import logging
from decouple import config

current_path = os.path.abspath(__file__)
parent_path = os.path.dirname(current_path)
grandparent_path = os.path.dirname(parent_path)


DB_CONFIG = {
    "host": config("DB_HOST"),
    "database": config("DB_NAME"),
    "user": config("DB_USER"),
    "password": config("DB_PASSWORD"),
    "port": config("DB_PORT"),
}

HEADERS_TEMPLATE = {
    'Host': 'magnit.ru',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Referer': 'https://magnit.ru/',
    'Origin': 'https://magnit.ru',
    'Cookie': '_ga_L0N0B74HJP=GS1.1.1733400269.3.1.1733400295.34.0.0; _ga=GA1.1.16636388.1729599468; _ym_uid=1729599469938378692; _ym_d=1729599469; mg_uac=1; mg_adlt=Y; KFP_DID=c8212aea-7fcb-a14f-a867-b01dec9a8df5; nmg_sp=Y; oxxfgh=8fd627e5-e0a4-4be4-a0b2-809d60cfa937#0#7884000000#5000#1800000#12840; x_shop_type=MM; mg_foradult=Y; cookies-modal=1; _ym_isad=2; _ym_visorc=b; mg_udi=7D219F1D-E8C9-5353-7A68-0495F554C728; nmg_udi=567FBEBF-6B50-FC1F-1F91-02A6F21D46AF; x_device_id=567FBEBF-6B50-FC1F-1F91-02A6F21D46AF',
}

POST_DATA_TEMPLATE = {
    "sort": {"order": "desc", "type": "popularity"},
    "pagination": {"limit": 50},
    "includeAdultGoods": True,
    "storeType": "1",
    "catalogType": "1"
}

py_logger = logging.getLogger("magnit_scraper")
py_logger.setLevel(logging.INFO)

# Обработчик для записи в файл
py_handler = logging.FileHandler(f"{grandparent_path}/logs/magnit_scraper.log", mode='w', encoding="utf-8")
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
console_handler.setFormatter(console_formatter)

# Добавляем оба обработчика к логгеру
py_logger.addHandler(py_handler)
py_logger.addHandler(console_handler)