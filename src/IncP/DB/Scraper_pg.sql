-- postgres
-- https://linuxhint.com/postgresql-full-text-search-tutorial


CREATE TABLE IF NOT EXISTS site(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_days         INTEGER DEFAULT 7,
    update_date         TIMESTAMP,
    url                 VARCHAR(64) NOT NULL,
    scheme              TEXT NOT NULL,
    scheme_date         DATE,
    robots              TEXT,
    sleep               FLOAT4 DEFAULT 3,
    sitemap             BOOLEAN DEFAULT FALSE,
    hours               VARCHAR(64),
    enabled             BOOLEAN DEFAULT FALSE,
    moderated           BOOLEAN DEFAULT FALSE,
    protected           BOOLEAN DEFAULT FALSE,
    UNIQUE (url)
);

CREATE TABLE IF NOT EXISTS site_ext(
    id                  SERIAL PRIMARY KEY,
    site_id             INTEGER,
    name                VARCHAR(24) NOT NULL,
    data                TEXT,
    enabled             BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (site_id) REFERENCES site(id),
    UNIQUE (site_id, name)
);

CREATE TABLE IF NOT EXISTS url(
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date         TIMESTAMP,
    site_id             INTEGER,
    url                 VARCHAR(256) NOT NULL,
    data_size           INTEGER DEFAULT 0,
    url_count           SMALLINT DEFAULT 0,
    status              SMALLINT,
    product_id          INTEGER,
    product_count       SMALLINT DEFAULT 0,
    timer               FLOAT4 DEFAULT 0,
    FOREIGN KEY (site_id) REFERENCES site(id),
    UNIQUE (url)
);

CREATE TABLE IF NOT EXISTS product (
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url_id              INTEGER,
    name                VARCHAR(128),
    price               FLOAT4,
    price_old           FLOAT4,
    price_cur           VARCHAR(3),
    image               VARCHAR(256),
    mpn                 VARCHAR(20),
    category            VARCHAR(30),
    stock               BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (url_id) REFERENCES url(id)
);

CREATE TABLE IF NOT EXISTS auth (
    id                  SERIAL PRIMARY KEY,
    auth_group_id       INTEGER,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_date          DATE,
    login               VARCHAR(16) NOT NULL,
    passw               VARCHAR(16),
    enabled             BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (auth_group_id) REFERENCES auth_group(id),
    UNIQUE (login)
);

CREATE TABLE IF NOT EXISTS auth_ext(
    id                  SERIAL PRIMARY KEY,
    auth_id             INTEGER,
    name                VARCHAR(24) NOT NULL,
    data                TEXT ,
    enabled             BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (auth_id) REFERENCES auth(id),
    UNIQUE (auth_id, name)
);

CREATE TABLE IF NOT EXISTS auth_group (
    id                  SERIAL PRIMARY KEY,
    create_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name                VARCHAR(16) NOT NULL,
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS auth_group_ext (
    id                  SERIAL PRIMARY KEY,
    auth_group_id       INTEGER,
    name                VARCHAR(24) NOT NULL,
    data                TEXT ,
    enabled             BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (auth_group_id) REFERENCES auth_group(id),
    UNIQUE (auth_group_id, name)
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
