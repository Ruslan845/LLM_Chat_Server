import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env.local")

def get_firebase_credentials():
    # Get the Base64 string from the environment variable
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS_BASERE")
    if not firebase_credentials:
        raise ValueError("FIREBASE_CREDENTIALS_BASERE environment variable is not set.")

    # Ensure Base64 string has proper padding
    firebase_credentials_padded = firebase_credentials + "=" * ((4 - len(firebase_credentials) % 4) % 4)

    try:
        # Decode the Base64 string and load it as JSON
        firebase_json = base64.b64decode(firebase_credentials_padded).decode("utf-8")
        return json.loads(firebase_json)
    except Exception as e:
        print(f"Error decoding FIREBASE_CREDENTIALS_BASERE: {e}")
        raise ValueError("Invalid FIREBASE_CREDENTIALS_BASERE environment variable. Ensure it is valid Base64.")

# Fetch and parse Firebase credentials
firebase_data = get_firebase_credentials()

# Initialize Firebase app using the credentials
cred = credentials.Certificate(firebase_data)
firebase_admin.initialize_app(cred)

def get_user_from_id_token(id_token):
    """
    Verify a Firebase ID token and return the decoded token.
    """
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
