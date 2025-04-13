# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.core.cache import cache # For Redis interactions
import traceback 

User = get_user_model()

# --- Token Validation Helper (Async) ---
@database_sync_to_async
def get_user_from_token(token_string):
    """
    Validates JWT token string and returns the associated user async.
    Handles database access asynchronously.
    Adjust validation logic based on your JWT library.
    """
    if not token_string:
        return None
    try:
        # Example using SimpleJWT AccessToken:
        token = AccessToken(token_string)
        user_id = token.get('user_id') # Use .get for safety
        if user_id is None:
             print("[get_user_from_token] Error: user_id not found in token payload.")
             return None

        # Fetch user from database
        user = User.objects.get(id=user_id)
        return user

    # Handle specific token errors
    except (TokenError, ValueError) as e: # ValueError for invalid token format
        print(f"[get_user_from_token] Token Error: {e}")
        return None
    # Handle database errors
    except User.DoesNotExist:
        print(f"[get_user_from_token] Error: User {user_id} not found.")
        return None
    # Handle other unexpected errors
    except Exception as e:
        print(f"[get_user_from_token] Unexpected Error: {e}")
        traceback.print_exc()
        return None

# --- Room Existence Helper (Async) ---
@database_sync_to_async
def room_exists(room_id):
    """Checks if a ChatRoom with the given room_id exists async."""
    if ChatRoom.objects is None: # Check if dummy class is used
         print("[room_exists] Warning: ChatRoom model not properly imported.")
         return False
    try:
        # UUID fields need to be validated or handled carefully
        return ChatRoom.objects.filter(room_id=room_id).exists()
    except ValueError: # Handle invalid UUID format if lookup fails
        print(f"[room_exists] Error: Invalid room_id format received: {room_id}")
        return False
    except Exception as e:
        print(f"[room_exists] Database Error: {e}")
        traceback.print_exc()
        return False


# --- Synchronous Redis Helper Functions ---

def sync_add_user_to_room_redis(room_id, user_id, channel_name):
    """Adds user and channel mapping to Redis using sync client."""
    user_id_str = str(user_id)
    members_key = f"chat:members:{room_id}"
    channels_key = f"chat:channels:{room_id}"
    print(f"[sync_add_user] Adding user {user_id_str} ({channel_name}) to Redis keys: {members_key}, {channels_key}")
    try:
        # Get sync client provided by django-redis
        redis_conn = cache.client.get_client(write=True) # Ensure write client
        if not redis_conn:
            print("[sync_add_user] Error: Failed to get Redis connection from cache.")
            return False
        # Use pipeline synchronously
        pipe = redis_conn.pipeline(transaction=True)
        pipe.sadd(members_key, user_id_str)
        pipe.hset(channels_key, user_id_str, channel_name)
        results = pipe.execute() # Executes synchronously
        print(f"[sync_add_user] Redis pipeline results: {results}")
        # Basic check: Ensure commands didn't error in pipeline (returns list of results)
        # Assumes success if results list is returned and has expected length
        return results is not None and len(results) == 2
    except Exception as e:
        print(f"[sync_add_user] Redis Error: {e}")
        traceback.print_exc()
        return False

def sync_remove_user_from_room_redis(room_id, user_id):
    """Removes user and channel mapping from Redis using sync client."""
    user_id_str = str(user_id)
    members_key = f"chat:members:{room_id}"
    channels_key = f"chat:channels:{room_id}"
    print(f"[sync_remove_user] Removing user {user_id_str} from Redis keys: {members_key}, {channels_key}")
    try:
        redis_conn = cache.client.get_client(write=True)
        if not redis_conn:
            print("[sync_remove_user] Error: Failed to get Redis connection.")
            return False
        pipe = redis_conn.pipeline(transaction=True)
        pipe.srem(members_key, user_id_str) # Remove from set
        pipe.hdel(channels_key, user_id_str) # Remove from hash
        results = pipe.execute()
        print(f"[sync_remove_user] Redis pipeline results: {results}")
        return results is not None and len(results) == 2
    except Exception as e:
        print(f"[sync_remove_user] Redis Error: {e}")
        traceback.print_exc()
        return False

def sync_get_room_member_count_redis(room_id):
    """Gets member count from Redis set using sync client."""
    members_key = f"chat:members:{room_id}"
    print(f"[sync_get_count] Getting SCARD for key: {members_key}")
    try:
        # Use read=True if you have replica configuration, else write=False or default
        redis_conn = cache.client.get_client(write=False)
        if not redis_conn:
            print("[sync_get_count] Error: Failed to get Redis connection.")
            return 0
        # Call SCARD synchronously (returns an integer)
        count = redis_conn.scard(members_key)
        print(f"[sync_get_count] SCARD result: {count}")
        return count if count is not None else 0 # Return 0 if key doesn't exist or error
    except Exception as e:
        print(f"[sync_get_count] Redis Error: {e}")
        traceback.print_exc()
        return 0

def sync_get_channel_for_user(room_id, target_user_id):
    """Gets channel name for a user ID from Redis Hash using sync client."""
    channels_key = f"chat:channels:{room_id}"
    target_user_id_str = str(target_user_id)
    print(f"[sync_get_channel] Getting HGET for key {channels_key}, field {target_user_id_str}")
    try:
        redis_conn = cache.client.get_client(write=False)
        if not redis_conn:
            print("[sync_get_channel] Error: Failed to get Redis connection.")
            return None
        # HGET returns bytes or None
        channel_name_bytes = redis_conn.hget(channels_key, target_user_id_str)
        if channel_name_bytes:
            channel_name = channel_name_bytes.decode('utf-8') # Decode bytes to string
            print(f"[sync_get_channel] Found channel: {channel_name}")
            return channel_name
        else:
            print(f"[sync_get_channel] Channel not found for user {target_user_id_str}")
            return None
    except Exception as e:
        print(f"[sync_get_channel] Redis Error: {e}")
        traceback.print_exc()
        return None

# --- End Sync Helpers ---


# --- Async Chat Consumer ---
class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections, messaging, and WebRTC signaling for chat rooms.
    Uses Redis via synchronous helpers wrapped in database_sync_to_async.
    """
    async def get_active_video_users(self):
        """Retrieves user IDs and usernames of users currently marked as streaming video."""
        active_users = []
        # This example assumes we store video status elsewhere, e.g., another Redis key or DB.
        # For simplicity now, let's just get all current members and assume frontend tracks status.
        # A more robust way would be needed for production.
        # Let's adapt to use the members set and channels hash for now.
        try:
            members_key = f"chat:members:{self.room_id}"
            channels_key = f"chat:channels:{self.room_id}"
            redis_conn = cache.client.get_client(write=False)
            if not redis_conn: return []

            member_ids_bytes = await database_sync_to_async(redis_conn.smembers)(members_key)
            member_ids = [mid.decode('utf-8') for mid in member_ids_bytes]

            if not member_ids: return []

            # Fetch usernames (inefficient for large rooms, consider storing usernames too)
            users = await database_sync_to_async(list)(User.objects.filter(id__in=member_ids).values('id', 'username'))
            user_map = {str(u['id']): u['username'] for u in users}

            # Return list of {'id': user_id, 'username': username} for current members
            # The *frontend* will need to know who among these has sent 'video_status: started'
            return [{'id': uid, 'username': user_map.get(uid, 'Unknown')} for uid in member_ids if uid in user_map]

        except Exception as e:
            print(f"[get_active_video_users] Error: {e}")
            traceback.print_exc()
            return []

    async def connect(self):
        """Handles new WebSocket connection attempts."""
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'

            # --- JWT Authentication & Room Validation ---
            query_string = self.scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            self.user = await get_user_from_token(token)

            if not self.user:
                print("[connect] Authentication failed.")
                await self.close(code=4001); return
            if not await room_exists(self.room_id):
                print(f"[connect] Room validation failed: {self.room_id}")
                await self.close(code=4004); return
            # --- End Validation ---

            print(f"[connect] User {self.user.username} (ID: {self.user.id}) attempting connection to room {self.room_id}...")

            # --- Join Channel Layer Group ---
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            print(f"[connect] User {self.user.username} added to group {self.room_group_name}")

            # --- Store User ID and Channel Name in Redis ---
            # Ensure this happens BEFORE reading count for broadcast
            added_to_redis = await database_sync_to_async(sync_add_user_to_room_redis)(
                self.room_id, self.user.id, self.channel_name
            )
            if not added_to_redis:
                print("[connect] CRITICAL: Failed to add user to Redis. Closing connection.")
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
                await self.close(code=4005)
                return
            # --- End Redis Update ---

            # --- Accept WebSocket connection ---
            # Accept AFTER essential setup like Redis add is done
            await self.accept()
            print(f"[connect] WebSocket connection accepted for {self.user.username}.")

            # --- Broadcasts *AFTER* accept and Redis update ---
            # This order increases likelihood that Redis SCARD reads the updated count
            print(f"[connect] Broadcasting join & count for {self.user.username}")

            # 1. Announce join to everyone *including self*
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message', 'message': f'{self.user.username} has joined.', 'username': 'System'
            })

            # 2. Broadcast the potentially updated member count to everyone *including self*
            # get_member_count will now read Redis AFTER self has been added
            await self.broadcast_member_count()

            # 3. Send current participant list ONLY to the newly connected user (using self.send)
            current_participants = await self.get_active_video_users()
            participants_for_self = [p for p in current_participants if str(p['id']) != str(self.user.id)]
            if participants_for_self:
                 await self.send(text_data=json.dumps({
                     'type': 'current_participants',
                     'participants': participants_for_self
                 }))
            # --- End Broadcasts ---

            print(f"[connect] User {self.user.username} connection fully established.")

        except Exception as e:
             print(f"[connect] Unexpected connection error for user {getattr(self, 'user', 'Unknown')}: {e}")
             traceback.print_exc()
             await self.close(code=4005)


    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        print(f"[disconnect] Connection closing with code: {close_code}")
        # Ensure user and room context exist before proceeding
        if hasattr(self, 'user') and self.user and hasattr(self, 'room_group_name'):
            user_id_str = str(self.user.id)
            print(f"[disconnect] User {self.user.username} ({user_id_str}) disconnecting from room {self.room_id}...")

            # --- Remove user from Redis state ---
            removed_from_redis = await database_sync_to_async(sync_remove_user_from_room_redis)(
                self.room_id, self.user.id
            )
            if not removed_from_redis:
                 print(f"[disconnect] WARNING: Failed to remove user {user_id_str} from Redis state.")
            # --- End Redis Update ---

            # Announce leave & broadcast updated count AFTER attempting removal
            print(f"[disconnect] Broadcasting leave & count for {self.user.username}")
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message', 'message': f'{self.user.username} has left.', 'username': 'System'
            })
            # Also announce video stopped if user leaves while potentially streaming
            await self.channel_layer.group_send(self.room_group_name, {
                 'type': 'video_status_broadcast', 'status': 'stopped',
                 'user_id': user_id_str, 'username': self.user.username,
                 'sender_channel': self.channel_name # Include sender for potential client-side exclusion
            })
            # Broadcast the final member count after departure
            await self.broadcast_member_count()

            # Leave Channel Layer group
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            print(f"[disconnect] User {self.user.username} removed from group {self.room_group_name}.")
        else:
             print("[disconnect] Disconnect called but user/room context missing.")


    async def receive(self, text_data=None, bytes_data=None):
        """Handles receiving messages from the WebSocket client."""
        if not text_data:
            print("[receive] Empty message received.")
            return
        if not hasattr(self, 'user') or not self.user:
             print("[receive] Message received from unidentified user (connection might be closing).")
             return

        print(f"[receive] Received message from {self.user.username}: {text_data[:100]}...") # Log snippet

        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                message = data.get('message', '').strip()
                if message:
                    print(f"[receive] Broadcasting chat message from {self.user.username}")
                    await self.channel_layer.group_send(
                        self.room_group_name, {
                            'type': 'chat_message', # Handled by chat_message method
                            'message': message,
                            'username': self.user.username,
                        }
                    )
                else:
                     print("[receive] Ignoring empty chat message.")

            elif message_type in ['webrtc_offer', 'webrtc_answer', 'webrtc_ice_candidate']:
                # Handle WebRTC signaling messages by relaying them
                await self.relay_webrtc_message(data)

            elif message_type == 'video_status':
                 # Handle user starting/stopping video broadcast
                 status = data.get('status')
                 if status in ['started', 'stopped']:
                     print(f"[receive] Broadcasting video status '{status}' for {self.user.username}")
                     # Broadcast the status change immediately
                     await self.channel_layer.group_send(self.room_group_name, {
                         'type': 'video_status_broadcast', # Handled by video_status_broadcast
                         'status': status,
                         'user_id': str(self.user.id),
                         'username': self.user.username,
                         'sender_channel': self.channel_name
                     })
                     # OPTIONAL: Immediately after, broadcast the updated list? Or rely on clients requesting it?
                     # For simplicity, let's stick to broadcasting only the status change for now.
                     # Frontend will need to manage its own list based on these messages.
                 else:
                      print(f"[receive] Ignoring invalid video status: {status}")

            else:
                # Handle unknown message types if necessary, or just log
                print(f"[receive] Unknown message type received: {message_type}")

        except json.JSONDecodeError:
            print(f"[receive] Malformed JSON received from {self.user.username}: {text_data[:100]}...")
            # Optionally send an error back to the client
            # await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON format.'}))
        except Exception as e:
             print(f"[receive] Error processing received message from {self.user.username}: {e}")
             traceback.print_exc()


    # --- WebRTC Relaying ---
    async def get_target_channel(self, target_user_id):
        """Looks up channel name using sync helper."""
        if not target_user_id: return None
        channel_name = await database_sync_to_async(sync_get_channel_for_user)(self.room_id, target_user_id)
        return channel_name

    async def relay_webrtc_message(self, event):
        """Relays WebRTC offer/answer/candidate to the target user's channel."""
        target_user_id = event.get('target_user_id')
        if not target_user_id:
            print("[relay_webrtc] Error: Missing target_user_id in event.")
            return

        # Ensure target is not the sender
        if str(target_user_id) == str(self.user.id):
             print(f"[relay_webrtc] Info: Sender {self.user.id} and target {target_user_id} are the same. Not relaying.")
             return

        target_channel_name = await self.get_target_channel(target_user_id)

        if target_channel_name:
            event_type = event.get('type', 'webrtc_message')
            print(f"[relay_webrtc] Relaying {event_type} from {self.user.id} to {target_user_id} via channel {target_channel_name}")
            # Add sender info so recipient knows who it's from
            event['sender_user_id'] = str(self.user.id)
            event['sender_username'] = self.user.username

            # Send directly to the target channel
            await self.channel_layer.send(
                target_channel_name,
                {
                    "type": "webrtc_relay", # MUST match a handler method name below
                    "event_data": event     # Pass the original event data, now including sender info
                }
            )
        else:
             # Target user might be offline or in Redis hash but channel disconnected
             print(f"[relay_webrtc] Warning: Target user {target_user_id} channel not found or inactive.")


    # --- Handler Methods (Called by channel_layer.group_send or channel_layer.send) ---

    async def chat_message(self, event):
        """Sends standard chat messages down the WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message', # Type for client-side handling
            'message': event['message'],
            'username': event['username'],
        }))

    async def chat_notification(self, event):
        """Sends general notifications (e.g., room deleted) down the WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'level': event.get('level', 'info'), # e.g., 'info', 'error', 'warning'
            'message': event['message'],
        }))

    async def member_count_update(self, event):
        """Sends the current member count down the WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'member_count',
            'count': event['count'],
        }))

    async def video_status_broadcast(self, event):
        """Sends video status updates (started/stopped) down the WebSocket."""
        # Optional: Exclude sending back to the originator on the client-side if needed,
        # based on matching event['user_id'] with the client's own ID.
        await self.send(text_data=json.dumps({
            'type': 'video_status', # Match client-side expected type
            'status': event['status'],
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def webrtc_relay(self, event):
        """
        Handler for messages sent directly to this channel via channel_layer.send.
        It forwards the nested WebRTC signaling data down the WebSocket.
        """
        relayed_data = event.get('event_data', {})
        event_type = relayed_data.get('type', 'unknown_webrtc')
        print(f"[webrtc_relay] Sending relayed {event_type} data down WebSocket to {self.user.username}.")
        await self.send(text_data=json.dumps(relayed_data))

    # This handler isn't strictly needed if only sent directly, but good practice
    async def current_participants(self, event):
         await self.send(text_data=json.dumps({
             'type': 'current_participants',
             'participants': event['participants']
         }))

    # --- Member Count Broadcaster ---
    async def broadcast_member_count(self):
        """Retrieves count via async helper and broadcasts it to the room group."""
        count = await self.get_member_count() # Calls async helper which wraps sync redis call
        print(f"[broadcast_member_count] Broadcasting count: {count} to group {self.room_group_name}")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'member_count_update', # Handled by member_count_update method
                'count': count,
            }
        )

    # --- Async Getter for Member Count (uses sync helper) ---
    async def get_member_count(self):
        """Async wrapper to get member count using the sync Redis helper."""
        count = await database_sync_to_async(sync_get_room_member_count_redis)(self.room_id)
        return count
