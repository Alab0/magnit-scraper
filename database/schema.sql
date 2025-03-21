CREATE TABLE store(
	id INT PRIMARY KEY,
	city VARCHAR(255) NOT NULL,
	address VARCHAR(255) NOT NULL
);

INSERT INTO store (id, city, address) VALUES 
(230972, 'Краснодар', 'ул. Шоссе Нефтяников'),
(774878, 'Москва', 'Таможенный проезд, д. 1/9'),
(524598, 'Нижний Новогород', 'ул. Молитовская, д. 7'),
(747996, 'Казань', 'ул. Пушкина, д. зд 13/52'),
(670926, 'Уфа', 'ул. Карла Маркса, д. 40'),
(610621, 'Ростов-на-дону', 'Ворошиловский пр-кт, д. 58'),
(784311, 'Санкт-Петербург', 'ул. Ижорская, д. 13/39'),
(543634, 'Новосибирск', 'ул. Котовского, д. 11');


CREATE TABLE category (
	id INT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	parent_id INT NULL,
	is_final BOOL NOT NULL
);

INSERT INTO category (id, name, parent_id, is_final) VALUES
(4834, 'Молоко, яйца, сыр', null, false),
(26995, 'Молоко, сливки', 4834, false),
(4840, 'Масло, маргарин', 4834, false),
(4854, 'Яйцо', 4834, false),
(4838, 'Кисломолочные продукты', 4834, false),
(4835, 'Йогурты и десерты', 4834, false),
(4839, 'Майонез', 4834, false),
(17487, 'Детские молочные продукты', 4834, false),
(37741, 'Сыры', 4834, false),
(45723, 'Молоко пастеризованное', 26995, true),
(45725, 'Молоко стерилизованное', 26995, true),
(18061, 'Молоко растительное', 26995, true),
(45729, 'Молоко с добавками', 26995, true),
(45727, 'Козье, топленое', 26995, true),
(992301, 'Сливки', 26995, true),
(17637, 'Масло', 4840, true),
(17639, 'Маргарин', 4840, true),
(4844, 'Сметана', 4838, true),
(45717, 'Традиционный творог', 4838, true),
(45715, 'Зерненый творог', 4838, true),
(45719, 'Мягкий творог', 4838, true),
(4837, 'Кефир', 4838, true),
(4842, 'Ряженка', 4838, true),
(18063, 'Тан, айран', 4838, true),
(27187, 'Другие кисломолочные продукты', 4838, true),
(38633, 'Йогурт', 4835, true),
(38637, 'Питьевой йогурт', 4835, true),
(17629, 'Творожки', 4835, true),
(45757, 'Творожные массы', 4835, true),
(17625, 'Сырки и снеки', 4835, true),
(4845, 'Коктейли и молочные напитки', 4835, true),
(38547, 'Пудинг', 4835, true),
(17673, 'Напитки для иммунитета', 4835, true),
(17621, 'Фруктовые десерты', 4835, true),
(17493, 'Молоко', 17487, true),
(17491, 'Кефир, ряженка', 17487, true),
(17489, 'Йогурты детские', 17487, true),
(17495, 'Творожные продукты', 17487, true),
(45761, 'Напитки для иммунитета', 17487, true),
(4847, 'Мягкие', 37741, true),
(4848, 'Плавленые', 37741, true),
(4849, 'Рассольные', 37741, true),
(4850, 'С плесенью', 37741, true),
(4851, 'Твёрдые', 37741, true),
(38037, 'Нарезка', 37741, true),
(47161, 'Алкоголь', null, false),
(41179, 'Вино', 47161, false),
(41181, 'Крепкий алкоголь', 47161, false),
(41183, 'Пиво, коктейли', 47161, false),
(41185, 'Тихие', 41179, true),
(41187, 'Игристые', 41179, true),
(41189, 'Крепленые и вермуты', 41179, true),
(41191, 'Фруктовые', 41179, true),
(41193, 'Водка', 41181, true),
(41195, 'Бренди', 41181, true),
(41197, 'Настойки', 41181, true),
(41199, 'Виски, бурбон', 41181, true),
(41201, 'Джин', 41181, true),
(41203, 'Ликеры', 41181, true),
(47261, 'Коньяк', 41181, true),
(47263, 'Ром', 41181, true),
(47265, 'Текила', 41181, true),
(47267, 'Бальзам', 41181, true),
(23293, 'Без алкоголя', 41183, true),
(41207, 'Россия', 41183, true),
(41209, 'Импорт', 41183, true),
(41211, 'Медовуха', 41183, true),
(47269, 'Коктейли', 41183, true),
(47271, 'Сидр', 41183, true),
(47565, 'Вкусовое', 41183, true),
(47567, 'Крафтовое', 41183, true);


CREATE TABLE product (
	id BIGINT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	price DECIMAL(10,2) NOT NULL,
	seo_code VARCHAR(255) NOT NULL,
	brand VARCHAR(255) NULL,
	manufacturer VARCHAR(255) NULL,
	category_id INT NOT NULL,
	CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE CASCADE
);


CREATE TABLE store_product (
	store_id INT NOT NULL,
	CONSTRAINT fk_store FOREIGN KEY (store_id) REFERENCES store (id) ON DELETE CASCADE,
	product_id BIGINT NOT NULL,
	CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE CASCADE,
	date DATE NOT NULL DEFAULT CURRENT_DATE,
	PRIMARY KEY (store_id, product_id, data)
);