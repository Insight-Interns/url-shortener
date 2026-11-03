# URL Shortener Database

Member-1 database contribution for the collaborative URL Shortener project.

## Contents

- `migrations/` - schema and index migrations
- `queries/` - URL lookup and analytics queries
- `seed/` - synthetic test data

## Migration Order

1. `001_create_url_mappings.sql`
2. `002_create_click_events.sql`
3. `003_create_indexes.sql`

## Local Development Setup

- Database: MySQL
- Database name: `url_shortener_db`
- Local development port: `3307`

Database credentials are not stored in this repository.

## Validated Behaviour

The local implementation has been tested for:

- URL mapping creation
- database-level unique short-code enforcement
- case-sensitive Base62-style short codes
- click-event insertion
- foreign-key relationship
- total-click analytics
- unique-click analytics
- device breakdown
- referrer breakdown

## Integration

The backend should obtain database credentials through environment/configuration variables.

Passwords and other secrets must not be hard-coded or committed to Git.
