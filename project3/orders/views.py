from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from . import views 
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')

    context = {
        "user": request.user
    }
    
    return render(request, 'home.html', context)

def signup(request):
    if request.method =='POST':
        username = request.POST["username"]
        password = request.POST["password"]
        name = request.POST["name"]
        email = request.POST["email"]
        user = User.objects.create_user(username, email, password)
        user.first_name = name
        user.save()
        return render(request, 'login.html',{"message": "You have successfully created an account. Thank you for registration. "})  
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, "home.html")
        else:
            return render(request, "login.html", {"message": "Invalid credentials."})

    return render(request, 'login.html')