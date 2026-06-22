-- ============================================================
-- FreshGrowth 테스트 데이터 시드 (기능 확인용)
--   - 판매자 3명 + 구매자 5명 (비밀번호 전부 '1234')
--   - 새 판매자 상품 6개
--   - COMPLETED 주문 ↔ 리뷰 쌍 (별점 2~5 분산, 여러 상품)
-- 주의: 1회용 시드. 재실행 시 주문·리뷰가 중복 생성됨(users는 email UNIQUE면 무시).
-- 실행: mysql -uroot -p1234 freshgrowth < seed_testdata.sql
-- ============================================================
USE freshgrowth;

-- 비밀번호 해시 = '1234' (기존 시드와 동일)
SET @pw = '$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O';

-- 1) 사용자: 판매자 3 + 구매자 5 -------------------------------------------------
INSERT INTO users(role, email, password, name) VALUES
  ('SELLER', 'seller_t1@test.com', @pw, '초록들녘농장'),
  ('SELLER', 'seller_t2@test.com', @pw, '동해바다수산'),
  ('SELLER', 'seller_t3@test.com', @pw, '햇살가득과수원'),
  ('BUYER',  'buyer_t1@test.com',  @pw, '박서준'),
  ('BUYER',  'buyer_t2@test.com',  @pw, '이지은'),
  ('BUYER',  'buyer_t3@test.com',  @pw, '최민호'),
  ('BUYER',  'buyer_t4@test.com',  @pw, '정유미'),
  ('BUYER',  'buyer_t5@test.com',  @pw, '강하늘');

SET @s1 = (SELECT user_id FROM users WHERE email='seller_t1@test.com');
SET @s2 = (SELECT user_id FROM users WHERE email='seller_t2@test.com');
SET @s3 = (SELECT user_id FROM users WHERE email='seller_t3@test.com');
SET @b1 = (SELECT user_id FROM users WHERE email='buyer_t1@test.com');
SET @b2 = (SELECT user_id FROM users WHERE email='buyer_t2@test.com');
SET @b3 = (SELECT user_id FROM users WHERE email='buyer_t3@test.com');
SET @b4 = (SELECT user_id FROM users WHERE email='buyer_t4@test.com');
SET @b5 = (SELECT user_id FROM users WHERE email='buyer_t5@test.com');

-- 2) 새 판매자 상품 6개 -----------------------------------------------------------
INSERT INTO products(seller_id, name, description, category, price, stock_qty, thumbnail_url, expiration_date) VALUES
  (@s1, '유기농 양파 1.5kg', '아삭한 친환경 양파',        'vegetable', 4800, 40, 'cdn.example.com', '2026-06-23'),
  (@s1, '친환경 깻잎 100g',  '향 좋은 무농약 깻잎',        'vegetable', 2200, 30, 'cdn.example.com', '2026-06-19'),
  (@s2, '손질 고등어 2손',   '당일 손질 국산 고등어',      'seafood',  11900, 25, 'cdn.example.com', '2026-06-20'),
  (@s2, '생물 오징어 3마리', '동해산 생물 오징어',         'seafood',   9800, 20, 'cdn.example.com', '2026-06-18'),
  (@s3, '햇사과 5입',        '아삭달콤 햇사과',            'fruit',    13500, 50, 'cdn.example.com', '2026-07-05'),
  (@s3, '꿀배 4입',          '과즙 가득 꿀배',             'fruit',    16000, 35, 'cdn.example.com', '2026-07-01');

SET @p_onion  = (SELECT product_id FROM products WHERE name='유기농 양파 1.5kg' ORDER BY product_id DESC LIMIT 1);
SET @p_mack   = (SELECT product_id FROM products WHERE name='손질 고등어 2손'   ORDER BY product_id DESC LIMIT 1);
SET @p_apple  = (SELECT product_id FROM products WHERE name='햇사과 5입'        ORDER BY product_id DESC LIMIT 1);

-- 3) 주문(COMPLETED) ↔ 리뷰 쌍 ---------------------------------------------------
--    공용 프로시저 대신, INSERT 주문 → LAST_INSERT_ID()로 즉시 리뷰 작성.
DELIMITER //
DROP PROCEDURE IF EXISTS seed_review //
CREATE PROCEDURE seed_review(IN p_buyer BIGINT, IN p_product BIGINT, IN p_rating INT, IN p_content VARCHAR(255))
BEGIN
  INSERT INTO orders(buyer_id, product_id, quantity, total_price, original_unit_price, status)
  VALUES (p_buyer, p_product, 1,
          (SELECT price FROM products WHERE product_id = p_product),
          (SELECT price FROM products WHERE product_id = p_product), 'COMPLETED');
  INSERT INTO reviews(order_id, rating, content) VALUES (LAST_INSERT_ID(), p_rating, p_content);
END //
DELIMITER ;

-- 기존 상품(1~13)에 리뷰 분산 (평균이 다양하게 나오도록 별점 섞음)
CALL seed_review(@b1, 1, 4, '잎이 싱싱하고 깨끗해요. 또 살게요.');
CALL seed_review(@b2, 1, 5, '상추 정말 신선합니다!');
CALL seed_review(@b3, 1, 3, '보통이에요. 양은 적당.');
CALL seed_review(@b4, 3, 4, '토마토 잘 익었어요.');
CALL seed_review(@b5, 3, 4, '달고 맛있네요.');
CALL seed_review(@b1, 6, 5, '한우 마블링 최고. 부드러워요.');
CALL seed_review(@b2, 6, 5, '구워 먹으니 살살 녹아요.');
CALL seed_review(@b3, 6, 4, '가격 대비 만족합니다.');
CALL seed_review(@b4, 6, 5, '재구매 의사 있어요!');
CALL seed_review(@b5, 7, 2, '시금치가 좀 시들었어요.');
CALL seed_review(@b1, 7, 3, '그럭저럭 먹을 만해요.');
CALL seed_review(@b2, 9, 4, '회 신선하고 두툼해요.');
CALL seed_review(@b3, 11, 5, '밥맛이 확실히 다릅니다.');
CALL seed_review(@b4, 11, 4, '20kg 가성비 좋아요.');
CALL seed_review(@b5, 13, 3, '바나나가 조금 익었어요.');
CALL seed_review(@b1, 13, 4, '아이가 잘 먹어요.');
CALL seed_review(@b2, 13, 2, '금방 물러서 아쉬워요.');

-- 새 판매자 상품에도 리뷰
CALL seed_review(@b3, @p_mack,  5, '고등어 비린내 없고 살이 탱탱!');
CALL seed_review(@b4, @p_mack,  4, '손질 잘 돼 있어 편해요.');
CALL seed_review(@b5, @p_apple, 5, '사과 아삭하고 달아요.');
CALL seed_review(@b1, @p_apple, 5, '아이 간식으로 최고.');
CALL seed_review(@b2, @p_apple, 5, '당도 훌륭합니다.');
CALL seed_review(@b3, @p_onion, 4, '양파 알이 굵어요.');
CALL seed_review(@b4, @p_onion, 3, '평범한 양파예요.');

DROP PROCEDURE IF EXISTS seed_review;

-- ============================================================
-- buyer@example.com(김도연) 떨이 구매 이력 — 절약액/회수매출 시연용
--   total_price = 떨이 결제액, original_unit_price = 정가
--   → 구매분석에서 절약액 = 정가×수량 − 결제액 이 양수로 집계됨
--   날짜를 분산해 월별 차트도 다양하게.
-- ============================================================
SET @bm = (SELECT user_id FROM users WHERE email='buyer@example.com');

DELIMITER //
DROP PROCEDURE IF EXISTS seed_deal //
CREATE PROCEDURE seed_deal(IN p_buyer BIGINT, IN p_product BIGINT, IN p_qty INT, IN p_discount INT, IN p_days_ago INT)
BEGIN
  DECLARE v_price INT;
  SELECT price INTO v_price FROM products WHERE product_id = p_product;
  INSERT INTO orders(buyer_id, product_id, quantity, total_price, original_unit_price, status, order_date)
  VALUES (p_buyer, p_product, p_qty,
          ROUND(v_price * p_qty * (100 - p_discount) / 100), -- 떨이 결제액(할인 적용)
          v_price,                                           -- 정가(단가)
          'COMPLETED',
          DATE_SUB(NOW(), INTERVAL p_days_ago DAY));
END //
DELIMITER ;

CALL seed_deal(@bm, 1,  2, 50,  3);   -- 무농약 청상추 ×2, 50% 떨이
CALL seed_deal(@bm, 4,  1, 35, 12);   -- 제주 노지 감귤, 35%
CALL seed_deal(@bm, 7,  1, 40, 20);   -- 시금치, 40%
CALL seed_deal(@bm, 9,  1, 30, 40);   -- 생물 오징어, 30%
CALL seed_deal(@bm, 12, 1, 20, 55);   -- 햇사과 5입, 20%

DROP PROCEDURE IF EXISTS seed_deal;

-- ============================================================
-- 폐기기간 옵션(product_lots) — 같은 상품도 남은 일수가 다른 로트는 할인율이 다르다.
--   상품마다 D-1(임박·큰 할인) / D-4(중간) / D-8(거의 정가) 3개 로트 생성.
--   가격은 상품 정가 기준, 옵션별 할인가는 WastePricingEngine이 조회 시 동적 계산.
-- ============================================================
INSERT INTO product_lots(product_id, expiration_date, stock_qty, price)
SELECT product_id, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  6,  price FROM products
UNION ALL
SELECT product_id, DATE_ADD(CURDATE(), INTERVAL 4 DAY),  10, price FROM products
UNION ALL
SELECT product_id, DATE_ADD(CURDATE(), INTERVAL 8 DAY),  16, price FROM products;
