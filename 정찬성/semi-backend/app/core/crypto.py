from functools import lru_cache

from cryptography.fernet import Fernet

from app.core.config import get_settings


@lru_cache
def _fernet() -> Fernet:
    key = get_settings().field_encryption_key
    if not key:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEY가 설정되지 않았습니다. "
            "'python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"' "
            "로 발급해 .env에 등록하세요."
        )
    return Fernet(key.encode())


def encrypt_field(plain_value: str) -> str:
    """parents_no_hp_enc / ban_hp_enc / teacher_hp_no_enc 등 개인정보 컬럼 암호화.
    레거시 AES_ENCRYPT(컬럼, 하드코딩키)를 대체 — 키는 반드시 환경변수로만 관리한다."""
    return _fernet().encrypt(plain_value.encode()).decode()


def decrypt_field(encrypted_value: str) -> str:
    return _fernet().decrypt(encrypted_value.encode()).decode()
