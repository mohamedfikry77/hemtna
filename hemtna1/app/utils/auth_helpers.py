from flask_jwt_extended import create_access_token
from datetime import timedelta

def generate_token(user_id, user_type):
    return create_access_token(
        identity={"id": user_id, "role": user_type},
        expires_delta=timedelta(days=7)
    )
