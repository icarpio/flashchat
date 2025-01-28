from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/private_chat/(?P<user1>\w+)_(?P<user2>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
]