# chat/views.py
from rest_framework import generics, permissions, status
from .models import ChatRoom
from .serializers import ChatRoomSerializer, ChatRoomCreateSerializer
from channels.layers import get_channel_layer # To send notifications
from asgiref.sync import async_to_sync 
from .permissions import IsOwnerOrReadOnly 
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model


User = get_user_model()
class ChatRoomListView(generics.ListAPIView):
    """
    API view to list all available chat rooms.
    Accessible by any user (authenticated or not).
    """
    queryset = ChatRoom.objects.all().order_by('-created_at')
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to see the rooms

class ChatRoomCreateView(generics.CreateAPIView):
    """
    API view to create a new chat room.
    Requires users to be authenticated.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users can create

    def get_serializer_context(self):
        """
        Pass the request context to the serializer.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a chat room instance.
    Only the creator can update or delete the room.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'room_id' # Use the UUID field for lookup

    async def broadcast_room_deleted(self, room_id):
        """Helper to notify WebSocket group."""
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_id}'
        await channel_layer.group_send(
            room_group_name,
            {
                'type': 'chat_notification', # New handler type in consumer
                'level': 'info',
                'message': 'This room has been deleted by the owner.',
            }
        )
        # Optionally, force disconnect clients after notification
        # await channel_layer.group_send(room_group_name, {'type': 'disconnect_clients'})


    def perform_destroy(self, instance):
        """
        Override perform_destroy to broadcast deletion before deleting.
        """
        room_id = str(instance.room_id) # Get room_id before instance is gone
        print(f"Room {instance.name} ({room_id}) is being deleted by {self.request.user.username}")

        # Broadcast the deletion message (using async_to_sync)
        async_to_sync(self.broadcast_room_deleted)(room_id)

        # Proceed with the default deletion
        instance.delete()
        print(f"Room {room_id} deleted from database.")




class TransferAdminView(APIView):
    """
    API view to transfer the admin rights (created_by) of a chat room.
    Only the current admin can perform this action.
    """
    permission_classes = [permissions.IsAuthenticated]

    async def broadcast_admin_change(self, room_id, old_admin_name, new_admin_name):
         """Helper to notify WebSocket group about admin change."""
         channel_layer = get_channel_layer()
         room_group_name = f'chat_{room_id}'
         await channel_layer.group_send(
             room_group_name,
             {
                 'type': 'chat_notification',
                 'level': 'info',
                 'message': f"Admin rights transferred from {old_admin_name} to {new_admin_name}.",
             }
         )

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, room_id=room_id)

        # Check if the requesting user is the current admin
        if room.created_by != request.user:
            return Response(
                {"error": "Only the current room admin can transfer ownership."},
                status=status.HTTP_403_FORBIDDEN
            )

        new_admin_username = request.data.get('new_admin_username')
        if not new_admin_username:
            return Response(
                {"error": "The 'new_admin_username' field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_admin = User.objects.get(username=new_admin_username)
        except User.DoesNotExist:
            return Response(
                {"error": f"User '{new_admin_username}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_admin == request.user:
             return Response(
                {"error": "Cannot transfer admin rights to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Optional Check: Is new admin a member? ---
        # If you added the 'members' field to ChatRoom and want to enforce this:
        if not room.members.filter(id=new_admin.id).exists():
           return Response(
               {"error": f"User '{new_admin_username}' is not a member of this room."},
               status=status.HTTP_400_BAD_REQUEST
           )
        # --- End Optional Check ---


        old_admin_name = room.created_by.username
        room.created_by = new_admin
        room.save()

        print(f"Admin for room {room.name} ({room_id}) transferred to {new_admin.username}")

        # Broadcast the change (using async_to_sync)
        async_to_sync(self.broadcast_admin_change)(
            str(room_id), old_admin_name, new_admin.username
        )

        # Return updated room data
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

