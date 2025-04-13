import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, auth

firebase_json = base64.b64decode(os.getenv("FIREBASE_CREDENTIALS_BASERE")).decode("utf-8")
firebase_data = json.loads(firebase_json)

# Path to your service account key JSON file
cred = credentials.Certificate(firebase_data)
firebase_admin.initialize_app(cred)

def get_user_from_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise ValueError("Invalid ID token")
    except auth.ExpiredIdTokenError:
        raise ValueError("Expired ID token")
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None