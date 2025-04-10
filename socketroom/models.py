# chat/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()

class ChatRoom(models.Model):
    """
    Represents a chat room where users can communicate.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Name of the chat room")
    # Using UUID for a unique, non-sequential room ID accessible via URL
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_by = models.ForeignKey(User, related_name='created_chat_rooms', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Consider adding a 'members' ManyToManyField if you need to track users explicitly
    members = models.ManyToManyField(User, related_name='chat_rooms', blank=True)

    def save(self, *args, **kwargs):
        # You might want to enforce uniqueness or other logic here
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name