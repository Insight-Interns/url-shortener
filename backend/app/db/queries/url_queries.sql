USE url_shortener_db;

-- ============================================================
-- URL Shortener - Core URL Mapping Queries
-- ============================================================

-- 1. Create a URL mapping
-- Backend supplies:
--   :id
--   :short_code
--   :original_url
--   :expires_at
--   :created_by
--
-- Example pattern:
--
-- INSERT INTO url_mappings (
--     id,
--     short_code,
--     original_url,
--     expires_at,
--     created_by
-- )
-- VALUES (
--     :id,
--     :short_code,
--     :original_url,
--     :expires_at,
--     :created_by
-- );


-- 2. Resolve active, non-expired short URL
SELECT
    id,
    short_code,
    original_url,
    created_at,
    expires_at
FROM url_mappings
WHERE short_code = 'Ab3xK91'
  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP(6));


-- 3. Find mapping by short code
SELECT
    id,
    short_code,
    original_url,
    created_at,
    expires_at,
    created_by
FROM url_mappings
WHERE short_code = 'Ab3xK91';


-- 4. List URL mappings
SELECT
    id,
    short_code,
    original_url,
    created_at,
    expires_at,
    created_by
FROM url_mappings
ORDER BY created_at DESC;


-- 5. Update expiry
-- UPDATE url_mappings
-- SET expires_at = :expires_at
-- WHERE id = :id;


-- 6. Delete mapping
-- Associated click_events are deleted automatically
-- through ON DELETE CASCADE.
--
-- DELETE FROM url_mappings
-- WHERE id = :id;
