from __future__ import annotations
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app


def _serializer():
    secret = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret_key=secret, salt="ngo-tool-security")

def make_token(payload: dict) -> str:
    s = _serializer()
    return s.dumps(payload)

def read_token(token: str, max_age_seconds: int) -> dict | None:
    s = _serializer()
    try:
        data = s.loads(token, max_age=max_age_seconds)
        return data
    except (BadSignature, SignatureExpired):
        return None