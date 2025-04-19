import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables from .env file
print("Loading environment variables...")
load_dotenv(dotenv_path=".env.local")

def get_firebase_credentials():
    """
    Fetches and decodes the Base64-encoded Firebase credentials
    from the environment variable.
    Returns:
        dict: Parsed Firebase credentials.
    Raises:
        ValueError: If the Base64 string is invalid or missing.
    """
    print("Fetching FIREBASE_CREDENTIALS_BASERE from environment variables...")
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS_BASERE")

    if not firebase_credentials:
        print("Environment variable FIREBASE_CREDENTIALS_BASERE is missing.")
        raise ValueError("FIREBASE_CREDENTIALS_BASERE environment variable is not set or missing.")

    # Add padding to the Base64 string if necessary
    print("Adding padding to Base64 credentials, if necessary...")
    firebase_credentials_padded = firebase_credentials + "=" * ((4 - len(firebase_credentials) % 4) % 4)

    try:
        # Decode the Base64 string and parse the JSON content
        print("Decoding Firebase credentials...")
        firebase_json = base64.b64decode(firebase_credentials_padded).decode("utf-8")
        print("Decoded credentials JSON:", firebase_json)
        return json.loads(firebase_json)
    except Exception as e:
        print(f"Error decoding Firebase credentials: {e}")
        raise ValueError(f"Failed to decode FIREBASE_CREDENTIALS_BASERE: {e}")

# Fetch and parse Firebase credentials
try:
    print("Attempting to fetch and decode Firebase credentials...")
    firebase_data = get_firebase_credentials()
    print("Firebase credentials successfully loaded.")
except ValueError as e:
    print(f"Error: {e}")
    raise

# Initialize Firebase app using the credentials
try:
    print("Initializing Firebase app...")
    cred = credentials.Certificate(firebase_data)
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase app: {e}")
    raise

def get_user_from_id_token(id_token):
    """
    Verifies a Firebase ID token and returns the decoded token.
    Args:
        id_token (str): Firebase ID token.
    Returns:
        dict: Decoded user information.
    Raises:
        ValueError: If the token is invalid or expired.
    """
    print(f"Verifying ID token: {id_token}...")
    try:
        decoded_token = auth.verify_id_token(id_token)
        print("Token verified successfully. Decoded token:", decoded_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        print("Invalid ID token.")
        raise ValueError("Invalid ID token")
    except auth.ExpiredIdTokenError:
        print("Expired ID token.")
        raise ValueError("Expired ID token")
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
