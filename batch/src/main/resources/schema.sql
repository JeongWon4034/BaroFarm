CREATE TABLE IF NOT EXISTS market_price (
    id BIGINT NOT NULL AUTO_INCREMENT,
    trade_date VARCHAR(20),
    market_name VARCHAR(100),
    item_name VARCHAR(100),
    item_code VARCHAR(50),
    kind_name VARCHAR(100),
    grade_name VARCHAR(50),
    unit_qty VARCHAR(50),
    avg_price INT,
    prev_avg_price INT,
    prev_year_price INT,
    fluctuation_rate VARCHAR(50),
    raw_json TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS market_report (
    id BIGINT NOT NULL AUTO_INCREMENT,
    report_date DATE NOT NULL,
    summary TEXT,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
