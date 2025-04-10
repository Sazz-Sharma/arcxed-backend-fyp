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
    async def connect(self):
        """
        Called when the WebSocket is handshaking as part of connection.
        """
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # --- JWT Authentication from Query String ---
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        self.user = None
        if token:
            self.user = await get_user_from_token(token)

        if not self.user:
            # User not authenticated or token invalid/missing
            print("WebSocket connection rejected: Invalid or missing token.")
            await self.close(code=4001) # Use a specific code for auth failure
            return
        

        # Check if the room exists (using an async helper)
        if not await self.room_exists(self.room_id):
            await self.close(code=4004) # Custom code for room not found
            return

        # Join the room group
        # channel_layer.group_add sends an event to a group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name # Unique channel name for this consumer instance
        )

        # Accept the WebSocket connection
        await self.accept()

        # Announce user joining (optional)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # Corresponds to the method name 'chat_message'
                'message': f'{self.user.username} has joined the room.',
                'username': 'System', # Indicate it's a system message
            }
        )

        print(f"User {self.user.username} connected to room {self.room_id} (channel {self.channel_name})")


    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        if hasattr(self, 'room_group_name'): # Ensure group name exists
            # Announce user leaving (optional)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username} has left the room.',
                    'username': 'System',
                }
            )

            # Leave the room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {self.user.username} disconnected from room {self.room_id} (channel {self.channel_name})")


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
        """
        Receives messages from the room group and sends them down the WebSocket.
        This method name (`chat_message`) matches the 'type' in group_send.
        """
        message = event['message']
        username = event['username']

        # Send message payload to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
        print(f"Sent message to {self.channel_name}: {message} (from {username})")


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