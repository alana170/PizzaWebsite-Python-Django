from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from . import views 

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')
    return render(request, 'home.html')

def signup(request):
    return render(request, 'signup.html')

