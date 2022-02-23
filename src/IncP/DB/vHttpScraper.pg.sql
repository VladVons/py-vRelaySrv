-- postgres
-- https://linuxhint.com/postgresql-full-text-search-tutorial

CREATE TABLE IF NOT EXISTS sites (
    id            SERIAL,
    create_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date   TIMESTAMP DEFAULT '2000-12-31',
    updated       BOOLEAN DEFAULT FALSE,
    update_days   INTEGER DEFAULT 7,
    url           VARCHAR(64),
    scheme        TEXT,
    tasks         INTEGER DEFAULT 4,
    sleep         INTEGER DEFAULT 1,
    enable        BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS urls (
    id            SERIAL,
    create_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url           VARCHAR(256),
    name          VARCHAR(128),
    price         FLOAT,
    price_old     FLOAT,
    image         VARCHAR(256),
    on_stock      BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS log (
    id            SERIAL,
    create_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type_id       INTEGER,
    descr         TEXT
);
