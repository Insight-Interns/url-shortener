import pytest
from datetime import timedelta
import time

from app.security.url_validator import (
    validate_and_sanitize_url,
    validate_custom_alias,
    URLSecurityError,
    is_ip_blocked,
)
from app.security.auth import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    decode_access_token,
    verify_resource_ownership,
    AuthSecurityError,
)
from app.security.rate_limiter import SlidingWindowRateLimiter
from app.services.analytics import (
    hash_ip_address,
    detect_device_type,
    sanitize_referrer,
)
from fastapi import HTTPException


class TestURLSecurity:
    """Tests for Phase 2: URL Security and SSRF Prevention."""

    def test_valid_http_and_https_urls(self):
        assert validate_and_sanitize_url("https://example.com/path", check_dns=False) == "https://example.com/path"
        assert validate_and_sanitize_url("http://example.org:8080/test?q=1", check_dns=False) == "http://example.org:8080/test?q=1"

    def test_reject_javascript_protocol(self):
        with pytest.raises(URLSecurityError, match="Only HTTP, HTTPS protocols are permitted"):
            validate_and_sanitize_url("javascript:alert(document.cookie)", check_dns=False)

    def test_reject_file_protocol(self):
        with pytest.raises(URLSecurityError, match="Only HTTP, HTTPS protocols are permitted"):
            validate_and_sanitize_url("file:///etc/passwd", check_dns=False)

    def test_reject_data_protocol(self):
        with pytest.raises(URLSecurityError, match="Only HTTP, HTTPS protocols are permitted"):
            validate_and_sanitize_url("data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==", check_dns=False)

    def test_reject_localhost_and_internal_hostnames(self):
        with pytest.raises(URLSecurityError, match="SSRF defense"):
            validate_and_sanitize_url("http://localhost/admin", check_dns=False)

        with pytest.raises(URLSecurityError, match="SSRF defense"):
            validate_and_sanitize_url("http://internal-service.local/api", check_dns=False)

    def test_reject_loopback_ip(self):
        assert is_ip_blocked("127.0.0.1") is True
        assert is_ip_blocked("127.0.1.1") is True
        assert is_ip_blocked("::1") is True

    def test_reject_cloud_metadata_ip(self):
        # AWS / GCP / Azure Instance Metadata Service (169.254.169.254)
        assert is_ip_blocked("169.254.169.254") is True
        assert is_ip_blocked("169.254.0.1") is True

    def test_reject_private_rfc1918_ips(self):
        assert is_ip_blocked("10.0.0.1") is True
        assert is_ip_blocked("172.16.0.5") is True
        assert is_ip_blocked("192.168.1.1") is True

    def test_allow_public_ips(self):
        assert is_ip_blocked("8.8.8.8") is False
        assert is_ip_blocked("1.1.1.1") is False

    def test_custom_alias_validation(self):
        assert validate_custom_alias("my-cool-link_2026") == "my-cool-link_2026"

        # Too short
        with pytest.raises(URLSecurityError, match="between 3 and 30 characters"):
            validate_custom_alias("ab")

        # Invalid characters
        with pytest.raises(URLSecurityError, match="invalid characters"):
            validate_custom_alias("link with spaces!")

        # Reserved alias
        with pytest.raises(URLSecurityError, match="reserved for system use"):
            validate_custom_alias("login")

        with pytest.raises(URLSecurityError, match="reserved for system use"):
            validate_custom_alias("api")


class TestAuthenticationSecurity:
    """Tests for Phase 3: Password Hashing, JWT, and Access Control."""

    def test_password_strength_enforcement(self):
        # Too short
        with pytest.raises(HTTPException):
            validate_password_strength("Short1!")

        # Missing digit
        with pytest.raises(HTTPException):
            validate_password_strength("NoDigitsHere!")

        # Missing uppercase
        with pytest.raises(HTTPException):
            validate_password_strength("alllowercase123")

        # Valid password
        validate_password_strength("SecureP@ssw0rd2026")

    def test_bcrypt_hashing_and_verification(self):
        raw_password = "SuperSecretPassword123"
        hashed = hash_password(raw_password)

        assert hashed != raw_password
        assert hashed.startswith("$2b$")
        assert verify_password(raw_password, hashed) is True
        assert verify_password("WrongPassword123", hashed) is False

    def test_jwt_token_lifecycle(self):
        user_id = "user-uuid-12345"
        token = create_access_token(subject=user_id, tier="registered")

        claims = decode_access_token(token)
        assert claims["sub"] == user_id
        assert claims["tier"] == "registered"
        assert claims["type"] == "access"

    def test_jwt_expiration(self):
        user_id = "user-uuid-expired"
        token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-10))

        with pytest.raises(AuthSecurityError, match="Token has expired"):
            decode_access_token(token)

    def test_object_ownership_enforcement(self):
        owner_id = "owner-uuid-111"
        different_user_id = "attacker-uuid-999"

        # Owner can access
        verify_resource_ownership(owner_id, owner_id)

        # Admin can access
        verify_resource_ownership(owner_id, different_user_id, is_admin=True)

        # Unauthorized user raises 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            verify_resource_ownership(owner_id, different_user_id, is_admin=False)
        assert exc_info.value.status_code == 403

        # Anonymous caller attempting to access owned resource raises 401
        with pytest.raises(HTTPException) as exc_info:
            verify_resource_ownership(owner_id, None)
        assert exc_info.value.status_code == 401


class TestRateLimiter:
    """Tests for Phase 4: Rate Limiting & Abuse Prevention."""

    def test_rate_limiter_allows_under_limit(self):
        test_limiter = SlidingWindowRateLimiter()
        key = "ip:198.51.100.10"
        limit = 5

        for _ in range(limit):
            allowed, remaining, max_limit, _ = test_limiter.is_allowed(key, limit)
            assert allowed is True

    def test_rate_limiter_blocks_over_limit(self):
        test_limiter = SlidingWindowRateLimiter()
        key = "ip:198.51.100.20"
        limit = 3

        # Exhaust quota
        for _ in range(limit):
            test_limiter.is_allowed(key, limit)

        # Next request must be blocked
        allowed, remaining, max_limit, reset_sec = test_limiter.is_allowed(key, limit)
        assert allowed is False
        assert remaining == 0
        assert reset_sec > 0


class TestAnalyticsPrivacy:
    """Tests for Analytics Security and Privacy Protection."""

    def test_ip_hashing_is_pseudonymous_and_salted(self):
        ip1 = "203.0.113.1"
        ip2 = "203.0.113.2"

        hash1 = hash_ip_address(ip1)
        hash2 = hash_ip_address(ip2)

        # Hashes must be 64-char SHA-256 strings
        assert len(hash1) == 64
        assert len(hash2) == 64
        assert hash1 != hash2
        # Plain IP never appears in the output
        assert ip1 not in hash1

    def test_device_classification(self):
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15"
        desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0"
        bot_ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

        assert detect_device_type(mobile_ua) == "Mobile"
        assert detect_device_type(desktop_ua) == "Desktop"
        assert detect_device_type(bot_ua) == "Bot"

    def test_referrer_sanitization_strips_sensitive_tokens(self):
        dirty_referrer = "https://partner.com/dashboard?token=secret123&session_id=abc&utm_source=twitter"
        clean = sanitize_referrer(dirty_referrer)

        assert "secret123" not in clean
        assert "token=" not in clean
        assert "utm_source=twitter" in clean

