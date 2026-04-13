import json
import os
import time

import jwt
import requests

try:
    from jwt.algorithms import RSAAlgorithm
except Exception:
    RSAAlgorithm = None


_JWKS_CACHE = {"ts": 0, "jwks": None}


def clerk_enabled():
    return os.environ.get("CLERK_ENABLED", "false").lower() in {"1", "true", "yes"}


def clerk_publishable_key():
    return os.environ.get("CLERK_PUBLISHABLE_KEY", "")


def clerk_frontend_api():
    explicit = os.environ.get("CLERK_FRONTEND_API", "").strip()
    if explicit:
        return explicit.replace("https://", "").replace("http://", "").rstrip("/")
    issuer = os.environ.get("CLERK_ISSUER", "").strip().rstrip("/")
    if issuer:
        return issuer.replace("https://", "").replace("http://", "").rstrip("/")
    return ""


def _jwks_url():
    explicit = os.environ.get("CLERK_JWKS_URL")
    if explicit:
        return explicit
    issuer = os.environ.get("CLERK_ISSUER", "").rstrip("/")
    if issuer:
        return f"{issuer}/.well-known/jwks.json"
    return ""


def _expected_issuer():
    return os.environ.get("CLERK_ISSUER", "").rstrip("/")


def _get_jwks():
    now = time.time()
    if _JWKS_CACHE["jwks"] and now - _JWKS_CACHE["ts"] < 3600:
        return _JWKS_CACHE["jwks"]
    url = _jwks_url()
    if not url:
        raise ValueError("CLERK_JWKS_URL or CLERK_ISSUER must be set for Clerk auth.")
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    jwks = resp.json()
    _JWKS_CACHE["ts"] = now
    _JWKS_CACHE["jwks"] = jwks
    return jwks


def verify_clerk_token(token):
    if RSAAlgorithm is None:
        raise RuntimeError(
            "PyJWT with algorithm support is required for Clerk token verification. "
            "Uninstall package 'jwt' if installed, then install 'PyJWT[crypto]'."
        )
    if not token:
        raise ValueError("Missing token.")
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("Token missing kid header.")
    keys = _get_jwks().get("keys", [])
    key_data = next((k for k in keys if k.get("kid") == kid), None)
    if not key_data:
        raise ValueError("No matching JWK found for token.")
    public_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
    kwargs = {
        "algorithms": ["RS256"],
        "options": {"verify_aud": False},
    }
    issuer = _expected_issuer()
    if issuer:
        kwargs["issuer"] = issuer
    return jwt.decode(token, public_key, **kwargs)
