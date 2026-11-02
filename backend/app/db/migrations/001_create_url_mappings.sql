USE url_shortener_db;

CREATE TABLE IF NOT EXISTS url_mappings (
    id CHAR(36) NOT NULL,

    short_code VARCHAR(7)
        CHARACTER SET ascii
        COLLATE ascii_bin
        NOT NULL,

    original_url TEXT NOT NULL,

    created_at TIMESTAMP(6)
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP(6),

    expires_at TIMESTAMP(6)
        NULL
        DEFAULT NULL,

    created_by CHAR(36)
        NULL,

    PRIMARY KEY (id),

    CONSTRAINT uq_url_mappings_short_code
        UNIQUE (short_code),

    CONSTRAINT chk_short_code_not_empty
        CHECK (CHAR_LENGTH(short_code) > 0)

) ENGINE=InnoDB
  DEFAULT CHARACTER SET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
