from rest_framework import serializers
from .models import UserProfile, Context


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user_id', 'username', 'groq_api_key', 'google_api_key']
        extra_kwargs = {
            'groq_api_key': {'write_only': True, 'required': False},
            'google_api_key': {'write_only': True, 'required': False},
        }


class ContextSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user_profile.user.username', read_only=True)

    class Meta:
        model = Context
        fields = ['id', 'user_profile', 'username', 'text', 'timestamp']
        read_only_fields = ['user_profile', 'timestamp']
