import datetime
import jwt
from os import path
import confuse

config = confuse.Configuration('App', __name__, read=False)
config_path = path.join(path.dirname(__file__), 'config.yaml')

config.set_file(config_path, base_for_paths=True)

SECRET_KEY = config['SECRET_KEY'].get()

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:

        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        return True, payload['sub']
    except jwt.ExpiredSignatureError:
        return False, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return False, 'Invalid token. Please log in again.'