USE url_shortener_db;

-- Sample URL with expiry
INSERT INTO url_mappings (
    id,
    short_code,
    original_url,
    expires_at,
    created_by
)
VALUES (
    UUID(),
    'Ab3xK91',
    'https://www.example.com/products/demo',
    DATE_ADD(NOW(), INTERVAL 30 DAY),
    NULL
);

-- Sample URL without expiry
INSERT INTO url_mappings (
    id,
    short_code,
    original_url,
    expires_at,
    created_by
)
VALUES (
    UUID(),
    'Test001',
    'https://www.example.org/documentation',
    NULL,
    NULL
);
