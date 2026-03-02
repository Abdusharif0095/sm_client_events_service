from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from lib.config import Keys
from authlib.jose import jwt
from typing import List
import time

app = FastAPI()
secret = Keys()

ACCESS_TOKEN_EXPIRATION = 360
REFRESH_TOKEN_EXPIRATION = 360 * 24 * 30
TOKEN_TYPES = {
    1: {"token_type": "access", "expiration": ACCESS_TOKEN_EXPIRATION},
    2: {"token_type": "refresh", "expiration": REFRESH_TOKEN_EXPIRATION},
}

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not self.verify_jwt(credentials.credentials, request):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=401, detail="Not authenticated.")

    def verify_jwt(self, jwtoken: str, request: Request) -> bool:
        isTokenValid: bool = False
        try:
            payload = jwt.decode(jwtoken, secret.publickey)

            if time.time() < payload['expires']:
                isTokenValid = True
            else:
                raise HTTPException(status_code=403, detail="Invalid token")
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            payload = None
        return isTokenValid

def generate_token(token_type: int, login: str, user: str, roles: list, device: str = None):
    token_data = TOKEN_TYPES.get(token_type)
    if not token_data:
        raise ValueError(f"Unsupported token type: {token_type}")
    device = device or "-1"
    payload = {
        "user_id": user,
        "user_login": login,
        "user_roles": roles,
        "device": device,
        "token_type": token_data["token_type"],
        "expires": time.time() + token_data["expiration"],
    }
    header = {'alg': 'RS256'}
    token = jwt.encode(header, payload, secret.privatekey)
    return token

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, secret.privatekey)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=403, detail="JWT decode error: {}".format(e))

def JWTpayload(credentials: str = Depends(JWTBearer())) -> dict:
    try:
        decoded_token = jwt.decode(credentials, secret.publickey)
        if decoded_token.get("token_type") != "access":
            raise HTTPException(status_code=403, detail="Invalid token type: must be access token")
        if time.time() > decoded_token["expires"]:
            raise HTTPException(status_code=401, detail="Token expired")
        
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=403, detail="JWT payload error: {}".format(e))

def RefreshJWTpayload(credentials: str = Depends(JWTBearer())) -> dict:
    try:
        decoded_token = jwt.decode(credentials, secret.publickey)
        if decoded_token.get("token_type") != "refresh":
            raise HTTPException(status_code=403, detail="Invalid token type: must be refresh token")
        if time.time() > decoded_token["expires"]:
            raise HTTPException(status_code=401, detail="Token expired")     
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=403, detail="JWT payload error: {}".format(e))