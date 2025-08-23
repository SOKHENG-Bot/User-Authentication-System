from passlib.context import CryptContext
import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, get_hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, get_hashed_password)


def encoded_token(data: dict, secret_key: str, algorithm: str):
    payload = data.copy()
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded_jwt


def decoded_token(token: str, secret_key: str, algorithms: list):
    payload = jwt.decode(token, secret_key, algorithms=algorithms)
    return payload
