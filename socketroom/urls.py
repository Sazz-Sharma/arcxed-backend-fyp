# chat/urls.py (for DRF API endpoints)
from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.ChatRoomListView.as_view(), name='chat-room-list'),
    path('rooms/create/', views.ChatRoomCreateView.as_view(), name='chat-room-create'),
    path('rooms/<uuid:room_id>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('rooms/<uuid:room_id>/transfer-admin/', views.TransferAdminView.as_view(), name='chat-room-transfer-admin'),

]