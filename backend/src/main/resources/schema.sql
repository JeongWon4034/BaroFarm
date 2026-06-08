CREATE DATABASE IF NOT EXISTS freshgrowth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE freshgrowth;

DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id BIGINT NOT NULL AUTO_INCREMENT,
    role VARCHAR(10) NOT NULL COMMENT 'BUYER | SELLER',
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE products (
    product_id BIGINT NOT NULL AUTO_INCREMENT,
    seller_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price INT NOT NULL,
    stock_qty INT NOT NULL DEFAULT 0,
    thumbnail_url VARCHAR(500),
    expiration_date DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);

CREATE TABLE orders (
    order_id BIGINT NOT NULL AUTO_INCREMENT,
    buyer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    total_price INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE reviews (
    review_id BIGINT NOT NULL AUTO_INCREMENT,
    order_id BIGINT NOT NULL UNIQUE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    PRIMARY KEY (review_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO users(role, email, password, name) VALUES
('SELLER', 'seller@example.com', '1234', '도연농장'),
('BUYER', 'buyer@example.com', '1234', '김도연');

-- 마감임박/떨이 데모용 시드 (기준일 2026-06-08, 유통기한 D-1~D-12로 분산)
INSERT INTO products(seller_id, name, description, category, price, stock_qty, thumbnail_url, expiration_date) VALUES
(1, '무농약 청상추',      '아침에 수확한 신선한 청상추.',   'vegetable', 3900,  48, NULL, '2026-06-09'), -- D-1, 재고많음 → HIGH
(1, '친환경 방울토마토',  '간식용 방울토마토.',             'vegetable', 5500,  50, NULL, '2026-06-09'), -- D-1, 재고만땅 → HIGH
(1, '완숙 토마토',        '산지 직송 달콤한 토마토.',       'vegetable', 6500,  30, NULL, '2026-06-10'), -- D-2
(1, '제주 노지 감귤 2kg', '새콤달콤 노지 감귤.',            'fruit',    12900,  20, NULL, '2026-06-11'), -- D-3
(1, '국산 손질 오징어',    '당일 손질한 오징어.',            'seafood',   8900,  15, NULL, '2026-06-13'), -- D-5
(1, '한우 불고기용 300g', '냉장 한우 불고기감.',            'meat',     18900,   8, NULL, '2026-06-16'), -- D-8
(1, '유기농 시금치',      '데쳐 먹기 좋은 시금치.',         'vegetable', 4200,  35, NULL, '2026-06-20'); -- D-12 → LOW
