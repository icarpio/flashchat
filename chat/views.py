from django.shortcuts import render
import json

def index(request):
    return render(request, 'chat/index.html')

def chat_rooms(request):
    return render(request, 'chat/index.html', {
        'username': request.user.username  # Pasa el username al template
    })

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': room_name,
        #'username': request.user.username   # Pasa el username al template
    })
