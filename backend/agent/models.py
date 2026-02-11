from django.db import models
from django.contrib.auth.models import User
import json # Import json for manual serialization/deserialization


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groq_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_api_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Context(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField()
    # Storing embedding as a TextField for SQLite compatibility
    embedding = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_embedding(self, data):
        self.embedding = json.dumps(data)

    def get_embedding(self):
        return json.loads(self.embedding) if self.embedding else None

    def __str__(self):
        return f"Context for {self.user_profile.user.username}: {self.text[:50]}..."

