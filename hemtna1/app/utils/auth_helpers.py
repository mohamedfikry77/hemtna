from flask_jwt_extended import create_access_token

def generate_token(user_id, user_type):
    additional_claims = {"role": user_type}
    return create_access_token(identity=str(user_id), additional_claims=additional_claims)
