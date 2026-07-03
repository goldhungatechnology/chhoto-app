"""
Public path policy file
"""

AUTH: list[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/signup",
    ## OAuth
    "/api/v1/auth/oauth/login/",
    "/api/v1/auth/oauth/callback/",
    ## Password
    "/api/v1/auth/password/forgot",
    "/api/v1/auth/password/forgot/verify",
]

COUNTRY: list[str] = ["/api/v1/countries"]


DUMMY: dict[str, list[str]] = {
    "/api/v1/dummy/dummy/": ["GET"],
}

OPENAPI: list[str] = ["/docs", "/openapi.json", "/redoc", "/metrics"]

SYSTEM: list[str] = ["/health", "/api/v1/health"]


PUBLIC_PATHS_METHODS: dict[str, list[str] | None] = {
    **dict.fromkeys(AUTH),
    **dict.fromkeys(OPENAPI),
    **dict.fromkeys(COUNTRY),
    **dict.fromkeys(SYSTEM),
    **DUMMY,
}


def is_public_path(path: str, method: str) -> bool:
    """
    Check if path/method should bypass authentication and access checks.

    Matching is exact by default. Only entries that explicitly end with a "/"
    (e.g. the OAuth provider routes ``/oauth/login/{provider}``) are treated as
    prefixes. This prevents an attacker from bypassing auth by appending to a
    public prefix (e.g. ``/api/v1/auth/login-admin`` or ``/openapi.json.evil``).
    """
    method = method.upper()
    normalized = path.rstrip("/")
    for public_path, methods in PUBLIC_PATHS_METHODS.items():
        if methods is not None and method not in methods:
            continue
        if public_path.endswith("/"):
            # Explicit prefix entry (requires something after the slash).
            if path.startswith(public_path):
                return True
        elif normalized == public_path.rstrip("/"):
            return True
    return False
