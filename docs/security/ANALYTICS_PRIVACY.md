# 📊 Analytics Privacy & Data Protection Specification

**Author**: Member 4 — Security Engineer (Anuj)  
**Applicability**: Analytics Data Pipeline, Redirection Handler, Database Retention  
**Compliance Target**: GDPR (Art. 5, Art. 6, Art. 32), ePrivacy Directive  

---

## 1. Principles of Analytics Data Processing

1. **Data Minimization (GDPR Art. 5(1)(c))**: We only collect the minimal technical metadata required to generate aggregate metrics (click counts, referrers, device types).
2. **Pseudonymization by Default (GDPR Art. 32(1)(a))**: Plaintext IP addresses are NEVER written to persistent storage or logs.
3. **No Cross-Site Tracking**: Analytics are strictly link-scoped and do not follow users across the internet or set persistent fingerprint cookies.
4. **Access Segregation**: Link metrics belong exclusively to the link's creator.

---

## 2. IP Address Salted Hashing Pipeline

Raw client IP addresses are considered Personal Identifiable Information (PII) under European data protection law. To ensure privacy while allowing unique visitor counting:

```mermaid
flowchart LR
    A["Incoming HTTP Request"] --> B["Extract Client IP (e.g. 203.0.113.195)"]
    B --> C["Append Secret Salt (ANALYTICS_SALT)"]
    C --> D["Compute SHA-256 Hash"]
    D --> E["Store ip_hash: 'a3f8c...64chars'"]
    B -.-> F["Discard Raw IP Immediately from Memory"]
```

### Properties of the Salted Hash
- **Irreversibility**: A one-way cryptographic SHA-256 hash prevents reversing the hash back to the visitor's IP address.
- **Salt Protection**: The server-side secret `ANALYTICS_SALT` prevents dictionary attacks and rainbow table precomputation.
- **Unique Counting**: The same visitor generating multiple clicks on the same link will produce the same `ip_hash`, enabling accurate `COUNT(DISTINCT ip_hash)` metrics without retaining PII.

---

## 3. Referrer & User-Agent Sanitization

### 3.1 Referrer Scrubbing
HTTP `Referer` headers frequently contain sensitive information (such as authorization tokens, API keys, or reset codes in the query string).
The sanitizer function `sanitize_referrer()`:
- Strips any query parameter containing substrings: `token`, `key`, `secret`, `auth`, `password`.
- Removes userinfo components (e.g., `https://user:pass@example.com/`).
- Caps referrer strings at 2,048 characters.

### 3.2 User-Agent Classification
Rather than storing verbose browser fingerprints that could facilitate canvas/browser fingerprinting, the raw User-Agent is categorized into high-level device groups:
- `Desktop`
- `Mobile`
- `Tablet`
- `Bot`

---

## 4. Access Control & Authorization (IDOR Prevention)

| Scenario | URL Ownership | Caller Role | Permission | HTTP Status |
| :--- | :--- | :--- | :--- | :--- |
| Registered User URL | Owned by User A (`created_by = A`) | User A (Authenticated) | **Allow** | `200 OK` |
| Registered User URL | Owned by User A (`created_by = A`) | User B (Authenticated) | **Deny** | `403 Forbidden` |
| Registered User URL | Owned by User A (`created_by = A`) | Anonymous Visitor | **Deny** | `401 Unauthorized` |
| Anonymous URL | Anonymous (`created_by = NULL`) | Any Visitor | **Allow** (Aggregate Stats) | `200 OK` |
| Any URL | Any Owner | Administrator (`tier = admin`) | **Allow** (System Audit) | `200 OK` |

---

## 5. Retention & Purging Policy

1. **Aggregated Summaries**: Retained indefinitely.
2. **Granular Click Records (`click_events`)**:
   - Individual click events older than **90 days** can be rolled up into daily summary tables and pruned via a scheduled cron cleanup job.
3. **Account Deletion**:
   - When a user deletes their account or URL, associated click events are automatically purged via MySQL `ON DELETE CASCADE` or anonymized via `ON DELETE SET NULL`.

