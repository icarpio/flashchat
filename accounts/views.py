from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el usuario con la contraseña hasheada
            messages.success(request, "Sing Up Success!")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})  # Plantilla

def logout_view(request):
    logout(request)  # Cierra sesión del usuario
    return redirect('login')  # Redirige al login después de cerrar sesión