USE url_shortener_db;

CREATE TABLE IF NOT EXISTS click_events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    url_mapping_id CHAR(36) NOT NULL,

    clicked_at TIMESTAMP(6)
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP(6),

    ip_hash CHAR(64) NULL,

    user_agent VARCHAR(512) NULL,

    referrer VARCHAR(2048) NULL,

    country_code CHAR(2) NULL,

    device_type VARCHAR(32) NULL,

    PRIMARY KEY (id),

    CONSTRAINT fk_click_events_url_mapping
        FOREIGN KEY (url_mapping_id)
        REFERENCES url_mappings(id)
        ON DELETE CASCADE

) ENGINE=InnoDB
  DEFAULT CHARACTER SET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
