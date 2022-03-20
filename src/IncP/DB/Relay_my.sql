CREATE TABLE IF NOT EXISTS `orgs` (
    `id`            INTEGER UNSIGNED AUTO_INCREMENT,
    `name`          VARCHAR(64),
    `address`       VARCHAR(64),
    `phone`         VARCHAR(13),
     PRIMARY KEY    (`id`)
);

CREATE TABLE IF NOT EXISTS `departs` (
    `id`            INTEGER UNSIGNED AUTO_INCREMENT,
    `name`          VARCHAR(64),
    `orgs_id`       INTEGER UNSIGNED,
    PRIMARY KEY     (`id`),
    FOREIGN KEY     (orgs_id) REFERENCES orgs(id)
);

CREATE TABLE IF NOT EXISTS `devices` (
    `id`            INTEGER UNSIGNED AUTO_INCREMENT,
    `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `expire_date`   DATE,
    `enable`        BOOLEAN DEFAULT FALSE,
    `uniq`          VARCHAR(16),
    `alias`         VARCHAR(16),
    `descr`         TEXT,
    `depart_id`     INTEGER UNSIGNED,
    PRIMARY KEY     (`id`),
    UNIQUE KEY      (`uniq`, `alias`),
    FOREIGN KEY     (depart_id) REFERENCES departs(id)
);

CREATE TABLE IF NOT EXISTS `devices_val` (
    `id`            INTEGER UNSIGNED AUTO_INCREMENT,
    `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `device_id`     INTEGER UNSIGNED,
    `val`           FLOAT(10,3),
    PRIMARY KEY     (`id`),
    FOREIGN KEY     (device_id) REFERENCES devices(id)
);

CREATE TABLE IF NOT EXISTS `log` (
    `id`            INTEGER UNSIGNED AUTO_INCREMENT,
    `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `type_id`       INTEGER UNSIGNED,
    `descr`         TEXT,
    PRIMARY KEY     (`id`)
);
