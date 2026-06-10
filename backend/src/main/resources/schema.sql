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
    intro VARCHAR(200),
    phone VARCHAR(20),
    profile_image MEDIUMTEXT,
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

CREATE TABLE wishlists (
    wishlist_id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (wishlist_id),
    UNIQUE KEY uq_wishlist (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE follows (
    follow_id BIGINT NOT NULL AUTO_INCREMENT,
    follower_id BIGINT NOT NULL,   -- 구매자
    following_id BIGINT NOT NULL,  -- 판매자
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follow_id),
    UNIQUE KEY uq_follow (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (following_id) REFERENCES users(user_id)
);

CREATE TABLE posts (
    post_id BIGINT NOT NULL AUTO_INCREMENT,
    author_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    view_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id),
    FOREIGN KEY (author_id) REFERENCES users(user_id)
);

CREATE TABLE comments (
    comment_id BIGINT NOT NULL AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(user_id)
);

-- 시드 비밀번호: '1234' (BCrypt cost=10, python bcrypt 생성)
INSERT INTO users(role, email, password, name) VALUES
('SELLER', 'seller@example.com', '$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O', '도연농장'),
('BUYER',  'buyer@example.com',  '$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O', '김도연');

-- 마감임박/떨이 데모용 시드 (기준일 2026-06-08, 유통기한 D-1~D-12로 분산)
INSERT INTO products(seller_id, name, description, category, price, stock_qty, thumbnail_url, expiration_date) VALUES
(1, '무농약 청상추',      '아침에 수확한 신선한 청상추.',   'vegetable', 3900,  48, NULL, '2026-06-09'), -- D-1, 재고많음 → HIGH
(1, '친환경 방울토마토',  '간식용 방울토마토.',             'vegetable', 5500,  50, NULL, '2026-06-09'), -- D-1, 재고만땅 → HIGH
(1, '완숙 토마토',        '산지 직송 달콤한 토마토.',       'vegetable', 6500,  30, NULL, '2026-06-10'), -- D-2
(1, '제주 노지 감귤 2kg', '새콤달콤 노지 감귤.',            'fruit',    12900,  20, NULL, '2026-06-11'), -- D-3
(1, '국산 손질 오징어',    '당일 손질한 오징어.',            'seafood',   8900,  15, NULL, '2026-06-13'), -- D-5
(1, '한우 불고기용 300g', '냉장 한우 불고기감.',            'meat',     18900,   8, NULL, '2026-06-16'), -- D-8
(1, '유기농 시금치',      '데쳐 먹기 좋은 시금치.',         'vegetable', 4200,  35, NULL, '2026-06-20'); -- D-12 → LOW

-- 게시판 데모 시드 (조회수·작성자·키워드 분산 → 검색/정렬/페이징 확인용)
INSERT INTO posts(author_id, title, content, view_count) VALUES
(1, '청상추 오래 보관하는 법 공유합니다',   '키친타월로 감싸 밀폐용기에 넣으면 일주일은 거뜬해요. 마감임박으로 산 상추도 이렇게 하면 안 버립니다.', 152),
(2, '토마토 후숙 꿀팁 있나요?',              '덜 익은 토마토 받았는데 빨리 익히는 방법 아시는 분?', 88),
(1, '제주 감귤 시세 요즘 어떤가요',          '노지 감귤 가격이 작년보다 오른 느낌인데 다들 어떻게 보시나요.', 47),
(2, '마감임박 떨이로 장 본 후기',            '한우 불고기감을 반값에 샀어요. 떨이 탭 자주 보게 되네요.', 230),
(1, '시금치 데치기 좋은 물 온도',            '끓는 물에 소금 약간, 30초면 충분합니다. 오래 데치면 물러져요.', 64),
(2, '오징어 손질 처음인데 무서워요',         '통오징어 손질 영상 추천 좀 부탁드립니다.', 39),
(1, '냉장고 채소칸 정리법',                  '채소별로 적정 습도가 달라요. 잎채소는 위, 뿌리채소는 아래.', 113),
(2, '방울토마토 아이 간식으로 굿',           '아이가 잘 먹어서 매주 삽니다. 당도 높은 농장 추천받아요.', 75),
(1, '산지 직거래의 좋은 점',                 '중간 유통이 없으니 더 신선하고 가격도 합리적입니다.', 201),
(2, '감귤 레시피 - 감귤청 만들기',           '껍질째 설탕에 재우면 향이 좋아요. 마감임박 감귤로 만들면 알뜰합니다.', 134),
(1, '한우 보관 온도 질문',                   '냉장이 좋을까요 냉동이 좋을까요. 3일 안에 먹을 거면 냉장?', 56),
(2, '버섯 종류별 손질법 정리',               '느타리는 결대로, 표고는 기둥 제거. 물에 오래 담그면 안 돼요.', 92),
(1, '요즘 제철 채소 뭐가 좋나요',            '6월에 맛있는 채소 추천 부탁드려요. 시금치 말고 또 뭐가 있을까요.', 78);

INSERT INTO comments(post_id, author_id, content) VALUES
(1, 2, '오 키친타월 꿀팁이네요. 바로 해볼게요!'),
(1, 1, '네 상추는 물기가 적이라 금방 무르더라고요.'),
(4, 1, '떨이 탭 반응이 좋아서 뿌듯합니다 :)'),
(9, 2, '확실히 직거래가 신선도가 다르긴 해요.'),
(10, 1, '감귤청 좋네요. 껍질 세척만 잘 하면 됩니다.');
