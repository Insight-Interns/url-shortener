USE url_shortener_db;

-- ============================================================
-- URL Shortener - Analytics Queries
-- ============================================================

-- 1. Record click event
--
-- INSERT INTO click_events (
--     url_mapping_id,
--     ip_hash,
--     user_agent,
--     referrer,
--     country_code,
--     device_type
-- )
-- VALUES (
--     :url_mapping_id,
--     :ip_hash,
--     :user_agent,
--     :referrer,
--     :country_code,
--     :device_type
-- );


-- 2. Total clicks
SELECT
    u.short_code,
    COUNT(c.id) AS total_clicks
FROM url_mappings u
LEFT JOIN click_events c
    ON c.url_mapping_id = u.id
WHERE u.short_code = 'Ab3xK91'
GROUP BY u.id, u.short_code;


-- 3. Unique clicks
SELECT
    u.short_code,
    COUNT(DISTINCT c.ip_hash) AS unique_clicks
FROM url_mappings u
LEFT JOIN click_events c
    ON c.url_mapping_id = u.id
WHERE u.short_code = 'Ab3xK91'
GROUP BY u.id, u.short_code;


-- 4. Clicks over time
SELECT
    DATE(c.clicked_at) AS click_date,
    COUNT(*) AS total_clicks,
    COUNT(DISTINCT c.ip_hash) AS unique_clicks
FROM click_events c
JOIN url_mappings u
    ON u.id = c.url_mapping_id
WHERE u.short_code = 'Ab3xK91'
GROUP BY DATE(c.clicked_at)
ORDER BY click_date;


-- 5. Device breakdown
SELECT
    c.device_type,
    COUNT(*) AS clicks
FROM click_events c
JOIN url_mappings u
    ON u.id = c.url_mapping_id
WHERE u.short_code = 'Ab3xK91'
GROUP BY c.device_type
ORDER BY clicks DESC;


-- 6. Country breakdown
SELECT
    c.country_code,
    COUNT(*) AS clicks
FROM click_events c
JOIN url_mappings u
    ON u.id = c.url_mapping_id
WHERE u.short_code = 'Ab3xK91'
GROUP BY c.country_code
ORDER BY clicks DESC;


-- 7. Referrer breakdown
SELECT
    c.referrer,
    COUNT(*) AS clicks
FROM click_events c
JOIN url_mappings u
    ON u.id = c.url_mapping_id
WHERE u.short_code = 'Ab3xK91'
GROUP BY c.referrer
ORDER BY clicks DESC;
