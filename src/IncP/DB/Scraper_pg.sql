-- postgres
-- https://linuxhint.com/postgresql-full-text-search-tutorial


CREATE TABLE IF NOT EXISTS site(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_days         INTEGER DEFAULT 7,
    update_date         TIMESTAMP DEFAULT "2000-12-31",
    url                 VARCHAR(64) UNIQUE NOT NULL,
    scheme              TEXT NOT NULL,
    scheme_date         DATE,
    robots              TEXT,
    sleep               FLOAT DEFAULT 3,
    sitemap             BOOLEAN DEFAULT FALSE,
    hours               VARCHAR(64),
    enabled             BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS url(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date         TIMESTAMP DEFAULT "2000-12-31",
    site_id             INTEGER,
    url                 VARCHAR(256) UNIQUE NOT NULL,
    data_size           INTEGER DEFAULT 0,
    url_count           SMALLINT DEFAULT 0,
    status              SMALLINT,
    product_id          INTEGER,
    FOREIGN KEY (site_id) REFERENCES site(id)
);

CREATE TABLE IF NOT EXISTS product(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url_id              INTEGER,
    name                VARCHAR(128),
    price               FLOAT,
    price_old           FLOAT,
    image               VARCHAR(256),
    on_stock            BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (url_id) REFERENCES url(id)
);

CREATE TABLE IF NOT EXISTS auth(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login               VARCHAR(16) UNIQUE NOT NULL,
    passw               VARCHAR(16),
    workers             SMALLINT DEFAULT 5,
    enabled             BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS proxy(
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(64) NOT NULL,
    enabled             BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS log(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type_id             INTEGER,
    descr               TEXT
);

-- procedures

CREATE OR REPLACE FUNCTION insert_product()
RETURNS TRIGGER AS $$
BEGIN
    update url
    set product_id = NEW.id, update_date = now()
    where (id = NEW.url_id);

    RETURN NULL;
END; $$ LANGUAGE "plpgsql";

create or replace trigger insert_product
    after insert on product
    for each row 
    execute procedure insert_product();
