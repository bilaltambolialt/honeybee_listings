-- =====================================================================
-- Business Listings Dashboard - database schema
-- Target: MySQL 8.0+ (developed on 9.7)
-- Safe to re-run: every statement uses IF NOT EXISTS.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS honeybee_listings
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- One-time app user setup (run as root; replace the password, never commit the real one):
-- CREATE USER 'listings_app'@'localhost' IDENTIFIED BY '<your_password>';
-- GRANT ALL PRIVILEGES ON honeybee_listings.* TO 'listings_app'@'localhost';

USE honeybee_listings;

CREATE TABLE IF NOT EXISTS listing_master (
    id             BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    business_name  VARCHAR(255)     NOT NULL,
    category       VARCHAR(100)     NOT NULL,
    city           VARCHAR(100)     NOT NULL,
    address        VARCHAR(500)     NULL,      -- some open-data records have no street address
    phone          VARCHAR(32)      NULL,      -- stored normalised, e.g. +91 98765 43210
    source         VARCHAR(50)      NOT NULL,  -- e.g. OpenStreetMap, Geoapify
    -- sha256 hex of normalised name|address|city|source, computed by the API.
    -- A fixed 64-char hash is used because a UNIQUE index across several long
    -- utf8mb4 text columns would exceed MySQL's index size limit.
    dedupe_key     CHAR(64)         NOT NULL,
    created_at     DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_listing_dedupe_key (dedupe_key),
    -- Dashboard endpoints GROUP BY these columns
    KEY idx_listing_city     (city),
    KEY idx_listing_category (category),
    KEY idx_listing_source   (source)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Cleaned business listings collected from multiple sources';
