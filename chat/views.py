from django.shortcuts import render
import json

def index(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': room_name  # Asegúrate de que solo pasas el nombre
    })
