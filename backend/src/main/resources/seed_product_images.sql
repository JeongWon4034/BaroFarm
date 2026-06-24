-- 자체호스팅 상품 이미지(네이버 검색 → frontend/public/seed-images 다운로드).
-- 배포 재현용: docker-entrypoint-initdb.d 04-images.sql 로 실행됨.
UPDATE products SET thumbnail_url='/seed-images/p1.jpg' WHERE product_id=1;
UPDATE products SET thumbnail_url='/seed-images/p2.jpg' WHERE product_id=2;
UPDATE products SET thumbnail_url='/seed-images/p3.jpg' WHERE product_id=3;
UPDATE products SET thumbnail_url='/seed-images/p4.jpg' WHERE product_id=4;
UPDATE products SET thumbnail_url='/seed-images/p5.jpg' WHERE product_id=5;
UPDATE products SET thumbnail_url='/seed-images/p6.jpg' WHERE product_id=6;
UPDATE products SET thumbnail_url='/seed-images/p7.jpg' WHERE product_id=7;
UPDATE products SET thumbnail_url='/seed-images/p8.jpg' WHERE product_id=8;
UPDATE products SET thumbnail_url='/seed-images/p9.jpg' WHERE product_id=9;
UPDATE products SET thumbnail_url='/seed-images/p10.jpg' WHERE product_id=10;
UPDATE products SET thumbnail_url='/seed-images/p11.jpg' WHERE product_id=11;
UPDATE products SET thumbnail_url='/seed-images/p12.jpg' WHERE product_id=12;
UPDATE products SET thumbnail_url='/seed-images/p13.jpg' WHERE product_id=13;
