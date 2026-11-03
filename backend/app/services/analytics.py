import hashlib
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings


def hash_ip_address(ip_str: str) -> str:
    """
    Computes an irreversible SHA-256 hash using a server-side privacy salt.
    Complies with GDPR and ePrivacy requirements by eliminating raw IP storage.
    Matches CHAR(64) ip_hash column in click_events schema.
    """
    if not ip_str:
        ip_str = "unknown"
    data = f"{ip_str}:{settings.ANALYTICS_SALT}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def detect_device_type(user_agent: str) -> str:
    """
    Analyzes User-Agent to determine device category without external bulky dependencies.
    """
    if not user_agent:
        return "Unknown"

    ua_lower = user_agent.lower()

    # Detect search engine / crawlers
    if any(bot in ua_lower for bot in ["bot", "crawl", "spider", "slurp", "facebookexternalhit"]):
        return "Bot"

    # Detect tablets
    if "ipad" in ua_lower or "tablet" in ua_lower:
        return "Tablet"

    # Detect mobile devices
    if any(mob in ua_lower for mob in ["mobile", "android", "iphone", "ipod", "windows phone"]):
        return "Mobile"

    return "Desktop"


def sanitize_referrer(referrer: Optional[str]) -> Optional[str]:
    """
    Sanitizes HTTP referrer URL:
    - Strips authentication credentials, tokens, or query parameters that may leak personal data.
    - Limits length to 2048 characters to match database constraints.
    """
    if not referrer:
        return None

    cleaned = referrer.strip()
    if len(cleaned) > 2048:
        cleaned = cleaned[:2048]

    try:
        parsed = urlparse(cleaned)
        # Drop username and password from referrer
        netloc = parsed.hostname or parsed.netloc
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        # Strip query params containing tokens/keys/passwords
        if parsed.query:
            params = parse_qs(parsed.query)
            safe_params = {
                k: v for k, v in params.items()
                if not any(secret_term in k.lower() for secret_term in ["token", "key", "secret", "auth", "pwd", "password"])
            }
            new_query = urlencode(safe_params, doseq=True)
        else:
            new_query = ""

        sanitized = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, new_query, ""))
        return sanitized
    except Exception:
        return cleaned[:512]


def extract_click_metadata(client_ip: str, user_agent: Optional[str], referrer: Optional[str]) -> Dict[str, Any]:
    """
    Extracts, sanitizes, and structures click event metadata ready for persistence.
    """
    clean_ua = (user_agent or "")[:512]
    return {
        "ip_hash": hash_ip_address(client_ip),
        "user_agent": clean_ua,
        "referrer": sanitize_referrer(referrer),
        "device_type": detect_device_type(clean_ua),
        "country_code": None,  # Can be populated via GeoIP/Cloudflare CF-IPCountry header
        "clicked_at": datetime.utcnow()
    }

