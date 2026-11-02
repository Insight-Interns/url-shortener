USE url_shortener_db;

CREATE INDEX idx_url_mappings_created_at
    ON url_mappings(created_at);

CREATE INDEX idx_url_mappings_expires_at
    ON url_mappings(expires_at);

CREATE INDEX idx_click_events_mapping_clicked
    ON click_events(url_mapping_id, clicked_at);

CREATE INDEX idx_click_events_mapping_ip_hash
    ON click_events(url_mapping_id, ip_hash);
