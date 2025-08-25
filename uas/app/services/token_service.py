import jwt
from datetime import datetime, timezone, timedelta

class TokenService:

    def generate_secure_token(self, payload: dict, secret_key: str, algorithm: str, expires_in: int) -> str:
        payload.update({"exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)})
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        return token
    
    def validate_secure_token(self, token: str, secret_key: str, algorithms: list) -> dict:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload

    def refresh_access_token(self):
        pass

    def revoke_token(self):
        pass

    def blacklist_token(self):
        pass