# URL Shortener Database ERD

## Current Member-1 Database Scope

```mermaid
erDiagram
    URL_MAPPINGS ||--o{ CLICK_EVENTS : records

    URL_MAPPINGS {
        CHAR36 id PK
        VARCHAR7 short_code UK
        TEXT original_url
        TIMESTAMP created_at
        TIMESTAMP expires_at
        CHAR36 created_by
    }

    CLICK_EVENTS {
        BIGINT id PK
        CHAR36 url_mapping_id FK
        TIMESTAMP clicked_at
        CHAR64 ip_hash
        VARCHAR512 user_agent
        VARCHAR2048 referrer
        CHAR2 country_code
        VARCHAR32 device_type
    }
```

## Relationship

One URL mapping can have zero or many click events.

`click_events.url_mapping_id` references `url_mappings.id`.

The foreign key uses `ON DELETE CASCADE`, so associated click events are removed when their URL mapping is deleted.

## Key Integrity Rule

`url_mappings.short_code` has a database-level UNIQUE constraint.

The short-code column uses ASCII binary collation so Base62-style values are case-sensitive.

For example:

- `Ab3xK91`
- `ab3xk91`

are treated as different short codes.
