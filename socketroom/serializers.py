# chat/serializers.py
from rest_framework import serializers
from .models import ChatRoom
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for listing ChatRoom instances.
    """
    created_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_id', 'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['room_id', 'created_by', 'created_at', 'created_by_username'] # User cannot set these directly

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating ChatRoom instances.
    """
    class Meta:
        model = ChatRoom
        fields = ['name'] # Only allow setting the name on creation

    def create(self, validated_data):
        # Assign the creator automatically based on the request user
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
             raise serializers.ValidationError("User must be authenticated to create a room.")

        room = ChatRoom.objects.create(created_by=request.user, **validated_data)
        return room