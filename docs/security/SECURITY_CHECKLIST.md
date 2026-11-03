# 📋 Security Checklist & Audit Verification

**Owner**: Member 4 — Security Engineer (Anuj)  
**Project**: URL Shortener Platform  
**Status**: Completed & Verified  

---

## Phase 1: Threat Modeling & Design
- [x] Identify attack surfaces (URL ingestion, Redirects, Auth, Stats, DB).
- [x] Create formal STRIDE Threat Model (`docs/security/THREAT_MODEL.md`).
- [x] Identify malicious URL scenarios (SSRF, protocol abuse, open redirect loops).
- [x] Review authentication approach (Stateless JWT + Bearer tokens + bcrypt).
- [x] Document privacy requirements for analytics (Salted SHA-256 pseudonymization).

---

## Phase 2: URL Security & SSRF Protection
- [x] Whitelist `http://` and `https://` protocols only (`url_validator.py`).
- [x] Reject `javascript:`, `file:`, `data:`, `vbscript:`, `blob:` protocols.
- [x] Enforce destination URL maximum size limit (2,048 characters).
- [x] Block loopback addresses (`127.0.0.0/8`, `::1`).
- [x] Block cloud instance metadata IP (`169.254.169.254`).
- [x] Block private RFC 1918 addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- [x] DNS pre-resolution validation to thwart DNS rebinding attacks.
- [x] Custom alias format verification (`^[a-zA-Z0-9_-]{3,30}$`).
- [x] Reserved route protection (`/api`, `/auth`, `/login`, `/stats`, etc.).

---

## Phase 3: Authentication & Access Control
- [x] Database migration for users (`004_create_users_table.sql`).
- [x] Secure password hashing using bcrypt with 12 work rounds (`auth.py`).
- [x] Password complexity enforcement (minimum 8 chars, uppercase, lowercase, digit).
- [x] Signed JWT token issuance with `HS256`, expiration, and `sub` UUID claims.
- [x] FastAPI Bearer dependency with automatic authentication failure handling.
- [x] Link ownership tracking (`created_by` mapped to `users.id`).
- [x] Insecure Direct Object Reference (IDOR) prevention on analytics: only the link owner can view stats.
- [x] Insecure Direct Object Reference (IDOR) prevention on link deletion: only the link owner can delete.

---

## Phase 4: Rate Limiting & Abuse Prevention
- [x] Sliding window rate limiter implemented (`rate_limiter.py`).
- [x] Tier-based rate thresholds:
  - Anonymous: 10 requests / hour per IP.
  - Registered: 100 requests / hour per user.
  - Premium: 10,000 requests / hour.
- [x] Return HTTP `429 Too Many Requests` when limit exceeded.
- [x] Provide `Retry-After` header and `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers.
- [x] Clean interface for drop-in Redis cluster backend for multi-instance deployments.

---

## Phase 5: Analytics Privacy & Security Testing
- [x] Visitor IP addresses are irreversibly hashed using SHA-256 and server-side salt (`ip_hash`).
- [x] Plaintext IP addresses are NEVER stored in the database.
- [x] Referrer URLs are sanitized to strip authentication tokens, passwords, and API keys.
- [x] Security headers middleware mounted:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- [x] Automated test suite verifying SSRF, protocol validation, password hashing, JWTs, rate limits, and analytics privacy (`backend/tests/test_security.py` & `backend/tests/test_api_endpoints.py`).

