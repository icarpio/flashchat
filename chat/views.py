from django.shortcuts import render
from .models import ChatRoom

def index(request):
     rooms = ChatRoom.objects.all()
     return render(request, 'chat/index.html', {
        'username': request.user.username,
        'rooms': rooms  # Pasa el username al template
    })



def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': room_name,
        'username': request.user.username
    })
