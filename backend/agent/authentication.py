import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.conf import settings
import os
import json
from .models import UserProfile # Import UserProfile

from .utils import init_firebase

# Inicializa o Firebase usando a lógica unificada do utils.py
init_firebase()


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
