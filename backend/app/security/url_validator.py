import ipaddress
import re
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional
from app.core.config import settings


class URLSecurityError(ValueError):
    """Custom exception raised when a URL fails security validation."""
    pass


# Reserved or private IP networks to block for SSRF prevention
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (local)
    ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918 Private
    ipaddress.ip_network("100.64.0.0/10"),      # Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link-local / Cloud metadata (AWS/GCP/Azure)
    ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),     # 6to4 Relay
    ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private
    ipaddress.ip_network("198.18.0.0/15"),      # Network benchmark tests
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved
    ipaddress.ip_network("255.255.255.255/32"), # Broadcast
    # IPv6
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("fc00::/7"),           # Unique local address
    ipaddress.ip_network("fe80::/10"),          # Link-local
    ipaddress.ip_network("ff00::/8"),           # Multicast
]


def is_ip_blocked(ip_str: str) -> bool:
    """Checks whether an IP address literal falls into private, loopback, or metadata ranges."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
    except ValueError:
        # Not an IP literal (it's a domain name)
        return False

    if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
        return True
    for network in BLOCKED_IP_NETWORKS:
        if ip_obj in network:
            return True
    return False


def validate_and_sanitize_url(url: str, check_dns: bool = True) -> str:
    """
    Comprehensive URL security validator:
    1. Enforces maximum length.
    2. Enforces HTTP/HTTPS protocol whitelist (rejects javascript:, file:, data:, etc.).
    3. Prevents SSRF attacks by blocking loopback, link-local (cloud metadata), and RFC1918 addresses.
    4. Normalizes URL formatting.
    """
    if not url or not isinstance(url, str):
        raise URLSecurityError("URL must be a non-empty string.")

    cleaned_url = url.strip()

    # 1. Length constraint
    if len(cleaned_url) > settings.MAX_URL_LENGTH:
        raise URLSecurityError(f"URL exceeds maximum allowed length of {settings.MAX_URL_LENGTH} characters.")

    # 2. Parse URL
    try:
        parsed = urlparse(cleaned_url)
    except Exception as e:
        raise URLSecurityError(f"Malformed URL structure: {str(e)}")

    scheme = parsed.scheme.lower()
    if scheme not in settings.ALLOWED_SCHEMES:
        raise URLSecurityError(
            f"Invalid protocol '{scheme}'. Only {', '.join(settings.ALLOWED_SCHEMES).upper()} protocols are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise URLSecurityError("URL is missing a valid domain hostname.")

    hostname_lower = hostname.lower()

    # Reject localhost & internal tlds
    if hostname_lower in ["localhost", "127.0.0.1", "::1"] or hostname_lower.endswith((".local", ".internal", ".localhost", ".test")):
        raise URLSecurityError(f"Access to local or internal host '{hostname}' is forbidden (SSRF defense).")

    # 3. Direct IP checking
    if is_ip_blocked(hostname_lower):
        raise URLSecurityError(f"Destination IP '{hostname}' resolves to a restricted internal address (SSRF blocked).")

    # 4. DNS resolution check (resolve host to IP to prevent DNS rebinding / internal routing)
    if check_dns:
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_found = item[4][0]
                if is_ip_blocked(ip_found):
                    raise URLSecurityError(
                        f"Domain '{hostname}' resolves to private/internal IP {ip_found} (SSRF blocked)."
                    )
        except socket.gaierror:
            # Unable to resolve hostname
            raise URLSecurityError(f"Domain '{hostname}' could not be resolved by DNS.")
        except URLSecurityError:
            raise
        except Exception as e:
            raise URLSecurityError(f"DNS validation error for '{hostname}': {str(e)}")

    return cleaned_url


def validate_custom_alias(alias: Optional[str]) -> Optional[str]:
    """
    Validates custom short code alias:
    1. Whitelist pattern: alphanumeric, hyphen, underscore.
    2. Length: between 3 and 30 chars.
    3. Protects reserved system routes (e.g. api, login, auth, stats).
    """
    if not alias:
        return None

    cleaned_alias = alias.strip()
    if not (settings.MIN_ALIAS_LENGTH <= len(cleaned_alias) <= settings.MAX_ALIAS_LENGTH):
        raise URLSecurityError(
            f"Custom alias must be between {settings.MIN_ALIAS_LENGTH} and {settings.MAX_ALIAS_LENGTH} characters."
        )

    if not re.match(r"^[a-zA-Z0-9_-]+$", cleaned_alias):
        raise URLSecurityError("Custom alias contains invalid characters. Use letters, numbers, hyphens, and underscores only.")

    if cleaned_alias.lower() in settings.RESERVED_ALIASES:
        raise URLSecurityError(f"The alias '{cleaned_alias}' is reserved for system use and cannot be claimed.")

    return cleaned_alias
