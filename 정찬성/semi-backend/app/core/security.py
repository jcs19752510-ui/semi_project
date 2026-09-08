import secrets

from pwdlib import PasswordHash

# FastAPI 공식 권장 조합(Argon2). 레거시 평문/MD5 비밀번호는 로그인 성공 시
# on-the-fly로 재해싱해 이 해시로 교체하는 방식(lazy migration)을 권장한다.
password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def issue_session_token() -> str:
    """세션 쿠키에 담을 토큰. DB에는 이 값 자체가 아니라 조회용으로만 저장하고,
    항상 서버 세션 저장소(DB/redis 등)와 대조해 검증한다."""
    return secrets.token_hex(32)
