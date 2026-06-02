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

INSERT INTO products(seller_id, name, description, category, price, stock_qty, thumbnail_url, expiration_date) VALUES
(1, '무농약 청상추', '아침에 수확한 신선한 청상추입니다.', 'vegetable', 3900, 42, 'https://cdn.example.com/lettuce.png', '2026-05-30'),
(1, '완숙 토마토', '산지에서 바로 보내는 달콤한 토마토입니다.', 'vegetable', 6500, 28, 'https://cdn.example.com/tomato.png', '2026-05-29');
