-- postgres
-- https://linuxhint.com/postgresql-full-text-search-tutorial

CREATE TABLE IF NOT EXISTS site (
    id            SERIAL PRIMARY KEY,
    create_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_days   INTEGER DEFAULT 7,
    url           VARCHAR(64),
    scheme        TEXT,
    tasks         INTEGER DEFAULT 4,
    sleep         INTEGER DEFAULT 1,
    enabled       BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS url (
    id            SERIAL PRIMARY KEY,
    update_date   TIMESTAMP DEFAULT '2000-12-31',
    site_id       INTEGER,
    url           VARCHAR(256),
    data_size     INTEGER,
    url_count     INTEGER,
    status        SMALLINT,
    is_product    BOOLEAN,
    FOREIGN KEY   (site_id) REFERENCES site(id)
);

CREATE TABLE IF NOT EXISTS product (
    id            SERIAL PRIMARY KEY,
    create_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url_id        INTEGER,
    name          VARCHAR(128),
    price         FLOAT,
    price_old     FLOAT,
    image         VARCHAR(256),
    on_stock      BOOLEAN DEFAULT TRUE,
    FOREIGN KEY   (url_id) REFERENCES url(id)
);

CREATE TABLE IF NOT EXISTS proxy (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(64),
    enabled       BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS log (
    id            SERIAL PRIMARY KEY,
    create_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type_id       INTEGER,
    descr         TEXT
);
