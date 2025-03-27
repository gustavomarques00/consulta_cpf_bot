import jwt
import os
import datetime

JWT_SECRET = os.getenv('JWT_SECRET', 'secretdoapp')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

def generate_token(user_id, cargo, expiration_years=5):
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=365 * expiration_years)
    payload = {"user_id": user_id, "cargo": cargo, "exp": expiration_date}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
