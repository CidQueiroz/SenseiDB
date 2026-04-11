import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.conf import settings
import os
import json
from .models import UserProfile # Import UserProfile

# --- Firebase Initialization (can be enhanced for production) ---
# Check if Firebase is already initialized
if not firebase_admin._apps:
    # Attempt to load credentials from environment variable first (e.g., in Cloud Run)
    google_application_credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

    if google_application_credentials_json:
        try:
            # Tenta carregar como JSON puro primeiro
            content = google_application_credentials_json.strip()
            
            # Se não começar com '{', pode ser Base64
            if not content.startswith('{'):
                import base64
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    if decoded.strip().startswith('{'):
                        content = decoded
                        print("🛠️ Firebase credentials detected as Base64 and decoded successfully.")
                except Exception as b64e:
                    print(f"DEBUG: Failed to decode as Base64: {b64e}")

            cred_dict = json.loads(content)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from environment variable.")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse credentials JSON: {e}")
            # Fallback a seguir...
            # Fallback to file if JSON is malformed
            current_dir = os.path.dirname(__file__)
            firebase_credentials_path = os.path.join(current_dir, "..", "firebase_credentials.json")
            if os.path.exists(firebase_credentials_path):
                cred = credentials.Certificate(firebase_credentials_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase initialized from file: {firebase_credentials_path}.")
            else:
                print(f"⚠️ firebase_credentials.json not found at {firebase_credentials_path}. Firebase features may be limited.")
    else:
        # Fallback to file if environment variable is not set
        current_dir = os.path.dirname(__file__)
        firebase_credentials_path = os.path.join(current_dir, "..", "firebase_credentials.json")
        if os.path.exists(firebase_credentials_path):
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            print(f"✅ Firebase initialized from file (fallback): {firebase_credentials_path}.")
        else:
            print(f"⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON not set and firebase_credentials.json not found at {firebase_credentials_path}. Firebase features may be limited.")


class FirebaseAuthentication(BaseAuthentication):
    """
    Custom authentication class to authenticate Firebase ID tokens.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        id_token = auth_header.split(' ').pop()
        if not id_token:
            return None

        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            print(f"❌ Firebase Auth Error: {e}") # Log detailed error to Cloud Run logs
            raise AuthenticationFailed(f'Invalid Firebase ID token: {e}')

        uid = decoded_token.get('uid')
        name = decoded_token.get('name', '')
        email = decoded_token.get('email', '')

        # Get or create Django user using an atomic transaction
        user, created = User.objects.get_or_create(
            username=uid,
            defaults={'email': email, 'first_name': name}
        )

        if created:
            user.set_unusable_password()
            user.save()

        # Ensure UserProfile exists for the user
        UserProfile.objects.get_or_create(user=user)

        return (user, None)
