CREATE DATABASE IF NOT EXISTS freshgrowth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE freshgrowth;

DROP TABLE IF EXISTS user_behavior_logs;
DROP TABLE IF EXISTS invalidated_tokens;
DROP TABLE IF EXISTS user_challenges;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS wishlists;
DROP TABLE IF EXISTS follows;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS product_lots;
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
-- products 는 '품목 마스터'(이름·카테고리·판매자). lot 이 있으면 price/stock_qty/expiration_date 는
-- 대표값일 뿐이고, 실제 판매 단위·가격·유통기한은 product_lots 가 권위를 가진다.

-- 폐기기간별 판매 옵션(lot). 같은 품목(새우젓)을 유통기한·재고·가격이 다른 여러 lot 으로 묶어
-- 목록은 품목 1장으로 간결하게, 상세에서 lot 별 떨이가를 골라 구매하게 한다.
CREATE TABLE product_lots (
    lot_id          BIGINT NOT NULL AUTO_INCREMENT,
    product_id      BIGINT NOT NULL,
    expiration_date DATE   NOT NULL,
    stock_qty       INT    NOT NULL DEFAULT 0,
    price           INT    NOT NULL,                 -- 이 lot 의 정가(떨이가는 WastePricingEngine 이 조회 시 계산)
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (lot_id),
    INDEX idx_lot_product (product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id BIGINT NOT NULL AUTO_INCREMENT,
    buyer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    lot_id BIGINT NULL,                              -- 구매한 폐기기간 옵션(lot). 레거시·상품단위 구매는 NULL
    quantity INT NOT NULL DEFAULT 1,
    total_price INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',   -- 판매자 처리 흐름: PENDING→CONFIRMED→SHIPPING→COMPLETED
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (lot_id) REFERENCES product_lots(lot_id)
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
    category VARCHAR(30) NOT NULL DEFAULT 'general' COMMENT 'general|recipe|tip|question|review',
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
    parent_id BIGINT NULL COMMENT '대댓글이면 부모 댓글 id(최상위는 NULL), 1-depth',
    author_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(comment_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(user_id)
);

-- 시드 비밀번호: '1234' (BCrypt cost=10, python bcrypt 생성)
INSERT INTO users(role, email, password, name) VALUES
('SELLER', 'seller@example.com', '$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O', '도연농장'),
('BUYER',  'buyer@example.com',  '$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O', '김도연');

-- 마감임박/떨이 데모용 시드 (유통기한을 오늘 기준 상대값으로 → 언제 실행해도 D-1~D-12 유지)
INSERT INTO products(seller_id, name, description, category, price, stock_qty, thumbnail_url, expiration_date) VALUES
(1, '무농약 청상추',      '아침에 수확한 신선한 청상추.',   'vegetable', 3900,  48, NULL, CURDATE() + INTERVAL 1 DAY),  -- D-1, 재고많음 → HIGH
(1, '친환경 방울토마토',  '간식용 방울토마토.',             'vegetable', 5500,  50, NULL, CURDATE() + INTERVAL 1 DAY),  -- D-1, 재고만땅 → HIGH
(1, '완숙 토마토',        '산지 직송 달콤한 토마토.',       'vegetable', 6500,  30, NULL, CURDATE() + INTERVAL 2 DAY),  -- D-2
(1, '제주 노지 감귤 2kg', '새콤달콤 노지 감귤.',            'fruit',    12900,  20, NULL, CURDATE() + INTERVAL 3 DAY),  -- D-3
(1, '국산 손질 오징어',    '당일 손질한 오징어.',            'seafood',   8900,  15, NULL, CURDATE() + INTERVAL 5 DAY),  -- D-5
(1, '한우 불고기용 300g', '냉장 한우 불고기감.',            'meat',     18900,   8, NULL, CURDATE() + INTERVAL 8 DAY),  -- D-8
(1, '유기농 시금치',      '데쳐 먹기 좋은 시금치.',         'vegetable', 4200,  35, NULL, CURDATE() + INTERVAL 12 DAY); -- D-12 → LOW

-- 게시판 데모 시드 (조회수·작성자·키워드 분산 → 검색/정렬/페이징 확인용)
INSERT INTO posts(author_id, category, title, content, view_count) VALUES
(1, 'tip',      '청상추 오래 보관하는 법 공유합니다',   '키친타월로 감싸 밀폐용기에 넣으면 일주일은 거뜬해요. 마감임박으로 산 상추도 이렇게 하면 안 버립니다.', 152),
(2, 'question', '토마토 후숙 꿀팁 있나요?',              '덜 익은 토마토 받았는데 빨리 익히는 방법 아시는 분?', 88),
(1, 'general',  '제주 감귤 시세 요즘 어떤가요',          '노지 감귤 가격이 작년보다 오른 느낌인데 다들 어떻게 보시나요.', 47),
(2, 'review',   '마감임박 떨이로 장 본 후기',            '한우 불고기감을 반값에 샀어요. 떨이 탭 자주 보게 되네요.', 230),
(1, 'tip',      '시금치 데치기 좋은 물 온도',            '끓는 물에 소금 약간, 30초면 충분합니다. 오래 데치면 물러져요.', 64),
(2, 'question', '오징어 손질 처음인데 무서워요',         '통오징어 손질 영상 추천 좀 부탁드립니다.', 39),
(1, 'tip',      '냉장고 채소칸 정리법',                  '채소별로 적정 습도가 달라요. 잎채소는 위, 뿌리채소는 아래.', 113),
(2, 'review',   '방울토마토 아이 간식으로 굿',           '아이가 잘 먹어서 매주 삽니다. 당도 높은 농장 추천받아요.', 75),
(1, 'general',  '산지 직거래의 좋은 점',                 '중간 유통이 없으니 더 신선하고 가격도 합리적입니다.', 201),
(2, 'recipe',   '감귤 레시피 - 감귤청 만들기',           '껍질째 설탕에 재우면 향이 좋아요. 마감임박 감귤로 만들면 알뜰합니다.', 134),
(1, 'question', '한우 보관 온도 질문',                   '냉장이 좋을까요 냉동이 좋을까요. 3일 안에 먹을 거면 냉장?', 56),
(2, 'recipe',   '버섯 종류별 손질법 정리',               '느타리는 결대로, 표고는 기둥 제거. 물에 오래 담그면 안 돼요.', 92),
(1, 'question', '요즘 제철 채소 뭐가 좋나요',            '6월에 맛있는 채소 추천 부탁드려요. 시금치 말고 또 뭐가 있을까요.', 78);

INSERT INTO comments(post_id, author_id, content) VALUES
(1, 2, '오 키친타월 꿀팁이네요. 바로 해볼게요!'),
(1, 1, '네 상추는 물기가 적이라 금방 무르더라고요.'),
(4, 1, '떨이 탭 반응이 좋아서 뿌듯합니다 :)'),
(9, 2, '확실히 직거래가 신선도가 다르긴 해요.'),
(10, 1, '감귤청 좋네요. 껍질 세척만 잘 하면 됩니다.');

-- ── 폐기 절감 챌린지 (마감임박 상품 구매로 음식물 폐기 줄이기) ─────────────
CREATE TABLE challenges (
    challenge_id BIGINT NOT NULL AUTO_INCREMENT,
    title        VARCHAR(200) NOT NULL,
    description  VARCHAR(500),
    goal_type    VARCHAR(40) NOT NULL DEFAULT 'DEADLINE_PURCHASE', -- 목표 유형(마감임박 상품 구매)
    goal_count   INT NOT NULL,                                     -- 달성 목표 횟수
    period_days  INT NOT NULL DEFAULT 7,
    badge_emoji  VARCHAR(8) DEFAULT '🥬',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (challenge_id)
);

CREATE TABLE user_challenges (
    user_challenge_id BIGINT NOT NULL AUTO_INCREMENT,
    user_id      BIGINT NOT NULL,
    challenge_id BIGINT NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'ONGOING',  -- ONGOING / COMPLETED
    progress     INT NOT NULL DEFAULT 0,
    joined_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    PRIMARY KEY (user_challenge_id),
    UNIQUE KEY uq_user_challenge (user_id, challenge_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id)
);

-- 행동 로그 (Layer 2 원천 데이터) — 퍼널·코호트·A/B 분석, AI 수요예측 피처의 출발점.
-- 적재 성능과 무결성 분리를 위해 user_id·product_id 에 FK 를 걸지 않는다(상품이 삭제돼도 과거 로그는 보존).
CREATE TABLE IF NOT EXISTS user_behavior_logs (
    log_id        BIGINT       NOT NULL AUTO_INCREMENT,
    session_id    VARCHAR(64)  NOT NULL,                    -- 퍼널 분석 기준 키
    user_id       BIGINT       NULL,                        -- 비로그인 NULL
    event_type    VARCHAR(30)  NOT NULL,                    -- view_home / click_product / view_detail / click_checkout / complete_order
    product_id    BIGINT       NULL,                        -- 이벤트 대상 상품
    ab_test_group VARCHAR(10)  NULL,                        -- A_GROUP / B_GROUP
    device_type   VARCHAR(15)  NULL,                        -- PC_WEB / MOBILE_WEB
    stay_duration INT          NULL,                        -- 페이지 체류 시간(초)
    occurred_at   DATETIME(3)  NOT NULL,                    -- 이벤트 발생 시각(서버 stamp)
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    INDEX idx_behavior_session (session_id),
    INDEX idx_behavior_event_type (event_type),
    INDEX idx_behavior_occurred_at (occurred_at)
);

-- 로그아웃·탈퇴 토큰 무효화 (DB 기반, 재시작·다중 인스턴스 안전)
CREATE TABLE IF NOT EXISTS invalidated_tokens (
    token_hash  VARCHAR(64)  NOT NULL,   -- SHA-256 hex (토큰 원문 저장 지양)
    expires_at  DATETIME     NOT NULL,   -- JWT 만료시각 — 이후 행 자동 정리 가능
    PRIMARY KEY (token_hash),
    INDEX idx_expires_at (expires_at)
);

INSERT INTO challenges(title, description, goal_type, goal_count, period_days, badge_emoji) VALUES
('알뜰 장보기 입문',   '마감임박 떨이 상품 1개 구매하기. 첫 폐기 절감 도전!',   'DEADLINE_PURCHASE', 1,  7,  '🌱'),
('이번 주 폐기 구원자', '마감임박 상품 3개를 구매해 음식물 폐기를 줄여보세요.',  'DEADLINE_PURCHASE', 3,  7,  '🦸'),
('폐기 절감 마스터',   '마감임박 상품 10개 구매로 진짜 절약왕 등극.',          'DEADLINE_PURCHASE', 10, 30, '🏆');
