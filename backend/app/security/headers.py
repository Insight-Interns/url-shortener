from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.security.auth import decode_access_token


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies security hardening HTTP headers to every incoming response
    and extracts Bearer token into request.state.user for rate-limiting & auth audit.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Pre-process: Extract optional auth token into request.state
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                claims = decode_access_token(token)
                request.state.user = claims
            except Exception:
                request.state.user = None
        else:
            request.state.user = None

        response = await call_next(request)

        # Apply hardened security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

