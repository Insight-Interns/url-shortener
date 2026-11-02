# URL Shortener Data Dictionary

## url_mappings

Stores the persistent mapping between a short code and its destination URL.

| Column | Type | Null | Constraint | Purpose |
|---|---|---|---|---|
| id | CHAR(36) | No | Primary Key | UUID identifier for URL mapping |
| short_code | VARCHAR(7) | No | UNIQUE | Base62-style short code |
| original_url | TEXT | No | | Destination/original URL |
| created_at | TIMESTAMP(6) | No | Default current timestamp | Creation timestamp |
| expires_at | TIMESTAMP(6) | Yes | | Optional expiry timestamp |
| created_by | CHAR(36) | Yes | | Optional creator/user identifier |

## click_events

Stores redirect/click events used for analytics.

| Column | Type | Null | Constraint | Purpose |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | No | Primary Key, Auto Increment | Click-event identifier |
| url_mapping_id | CHAR(36) | No | Foreign Key | Associated URL mapping |
| clicked_at | TIMESTAMP(6) | No | Default current timestamp | Click timestamp |
| ip_hash | CHAR(64) | Yes | | Hashed IP-derived identifier |
| user_agent | VARCHAR(512) | Yes | | Client/browser information |
| referrer | VARCHAR(2048) | Yes | | Referring URL |
| country_code | CHAR(2) | Yes | | Optional country code |
| device_type | VARCHAR(32) | Yes | | Optional device category |

## Foreign Key

`click_events.url_mapping_id` references `url_mappings.id` with `ON DELETE CASCADE`.

## Current Analytics Supported

- Total clicks
- Unique clicks
- Clicks over time
- Device breakdown
- Country breakdown
- Referrer breakdown
