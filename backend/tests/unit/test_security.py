import pytest
from app.core.security import hash_password, verify_password, mask_pii, create_access_token, decode_token


def test_password_hash_and_verify():
    password = "MySecurePass123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_mask_pii_tc():
    text = "TC kimliğim 12345678901 ve telefon 05321234567"
    masked = mask_pii(text)
    assert "12345678901" not in masked
    assert "05321234567" not in masked
    assert "***********" in masked


def test_mask_pii_email():
    text = "Email adresim john.doe@example.com"
    masked = mask_pii(text)
    assert "john.doe@example.com" not in masked
    assert "***@***" in masked


def test_mask_pii_phone_with_country_code():
    text = "Beni +905321234567 numaram ile ara"
    masked = mask_pii(text)
    assert "+905321234567" not in masked


def test_jwt_create_and_decode():
    import uuid
    user_id = uuid.uuid4()
    token = create_access_token(user_id, {"role": "operator"})
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert payload["role"] == "operator"


def test_jwt_invalid_token():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        decode_token("invalid.token.here")
    assert exc.value.status_code == 401
