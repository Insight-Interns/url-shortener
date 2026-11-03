USE url_shortener_db;

-- ============================================================
-- Member 4 (Security Engineer) - Users Table & Access Control
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NULL,
    tier ENUM('registered', 'premium', 'admin') NOT NULL DEFAULT 'registered',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email),
    INDEX idx_users_email (email)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- Optional Foreign Key linking url_mappings.created_by to users.id
-- Uses ON DELETE SET NULL to preserve link history if a user is deleted
ALTER TABLE url_mappings
    ADD CONSTRAINT fk_url_mappings_created_by
    FOREIGN KEY (created_by)
    REFERENCES users(id)
    ON DELETE SET NULL;

