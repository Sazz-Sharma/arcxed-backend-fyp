# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # For interacting with Django models asynchronously
from .models import ChatRoom
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication # Or your custom JWT auth class
from django.conf import settings
from django.core.cache import cache

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_string):
    """
    Helper function to retrieve user from JWT token.
    """
    try:
        # SimpleJWT Example: Decode the token
        token = AccessToken(token_string)
        # SimpleJWT Example: Get user ID from token
        user_id = token['user_id'] # Adjust field name if your payload is different
        user = User.objects.get(id=user_id)
        return user
    except (TokenError, User.DoesNotExist, KeyError):
        # Handle invalid token, user not found, or bad payload
        return None
    except Exception as e:
        # Log other potential errors
        print(f"Error validating token: {e}")
        return None
    


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for chat rooms.
    """
    def get_redis_key(self):
        """Generates the Redis key for tracking members in this room."""
        return f"chat:members:{self.room_id}"

    async def get_member_count(self):
        """Gets the current member count from Redis."""
        redis_key = self.get_redis_key()
        # Use cache.connection.scard for Redis specific command SCARD
        # Requires using django-redis backend for cache 'default'
        try:
            # Access the underlying redis client connection
            redis_conn = cache.client.get_client()
            count = await redis_conn.scard(redis_key)
            return count
        except Exception as e:
            print(f"Error accessing Redis SCARD for key {redis_key}: {e}")
            return 0 # Default to 0 on error

    async def broadcast_member_count(self):
        """Broadcasts the current member count to the group."""
        count = await self.get_member_count()
        print(f"Broadcasting member count for room {self.room_id}: {count}")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'member_count_update', # New handler type
                'count': count,
            }
        )

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # --- JWT Authentication from Query String ---
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        self.user = None
        if token:
            self.user = await get_user_from_token(token)
        # ... (room_id, group_name, token auth logic as before) ...
        if not self.user:
            await self.close(code=4001)
            return
        if not await self.room_exists(self.room_id):
            await self.close(code=4004)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # --- Add user to Redis Set ---
        try:
            redis_key = self.get_redis_key()
            redis_conn = cache.client.get_client()
            await redis_conn.sadd(redis_key, str(self.user.id)) # Store user ID as string
            print(f"User {self.user.id} added to Redis set {redis_key}")
        except Exception as e:
             print(f"Error adding user to Redis set {redis_key}: {e}")
        # --- End Redis Add ---

        # Accept connection
        await self.accept()

        # Announce user joining
        await self.channel_layer.group_send(
            self.room_group_name,
            { 'type': 'chat_message', 'message': f'{self.user.username} has joined.', 'username': 'System' }
        )

        # Broadcast updated member count
        await self.broadcast_member_count()

        print(f"User {self.user.username} connected to room {self.room_id}")

    async def disconnect(self, close_code):
         if hasattr(self, 'room_group_name') and hasattr(self, 'user') and self.user:
            print(f"User {self.user.username} disconnecting from room {self.room_id}")
            # --- Remove user from Redis Set ---
            try:
                redis_key = self.get_redis_key()
                redis_conn = cache.client.get_client()
                await redis_conn.srem(redis_key, str(self.user.id))
                print(f"User {self.user.id} removed from Redis set {redis_key}")
            except Exception as e:
                print(f"Error removing user from Redis set {redis_key}: {e}")
            # --- End Redis Remove ---

            # Announce user leaving
            await self.channel_layer.group_send(
                self.room_group_name,
                { 'type': 'chat_message', 'message': f'{self.user.username} has left.', 'username': 'System' }
            )

            # Broadcast updated member count AFTER announcing departure
            await self.broadcast_member_count()

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {self.user.username} disconnected.")


    async def receive(self, text_data=None, bytes_data=None):
        """
        Called when the server receives a message from the WebSocket.
        """
        if not text_data:
            return # Ignore empty messages

        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Basic validation
            if not isinstance(message, str) or not message.strip():
                print(f"Received invalid message format from {self.user.username}")
                return

        except (json.JSONDecodeError, KeyError):
             print(f"Received malformed JSON from {self.user.username}: {text_data}")
             # Optionally send an error back to the client
             await self.send(text_data=json.dumps({
                 'error': 'Invalid message format. Send JSON with a "message" key.'
             }))
             return

        # Get username from the authenticated user
        username = self.user.username

        # Send the received message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # Event type handled by chat_message method
                'message': message,
                'username': username,
            }
        )
        print(f"Received message from {username} in room {self.room_id}: {message}")


    # --- Handler methods for events sent to the group ---
    async def chat_message(self, event):
        # ... (no change needed here) ...
        await self.send(text_data=json.dumps({
            'type': 'message', # Add a type field for frontend routing
            'message': event['message'],
            'username': event['username'],
        }))

    async def chat_notification(self, event):
        """Handles sending general notifications to the client."""
        await self.send(text_data=json.dumps({
            'type': 'notification', # Add a type field
            'level': event.get('level', 'info'), # e.g., 'info', 'error'
            'message': event['message'],
        }))

    async def member_count_update(self, event):
        """Handles sending the member count to the client."""
        await self.send(text_data=json.dumps({
            'type': 'member_count', # Add a type field
            'count': event['count'],
        }))

    # Optional: Handler to force disconnection (called from perform_destroy)
    async def disconnect_clients(self, event):
       print(f"Force closing connection {self.channel_name} for room {self.room_id}")
       await self.close(code=4012) # Custom code for room deleted

    # --- Async Database Helper ---

    @database_sync_to_async
    def room_exists(self, room_id):
        """
        Checks if a ChatRoom with the given room_id (UUID) exists.
        Uses database_sync_to_async to safely interact with the ORM.
        """
        try:
            # UUID fields need to be validated or handled carefully
            return ChatRoom.objects.filter(room_id=room_id).exists()
        except ValueError: # Handle invalid UUID format
            return False