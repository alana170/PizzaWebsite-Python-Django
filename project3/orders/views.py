from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from . import views 
from django.contrib.auth.models import User
from orders.models import Product, ProductCategory, OrderMain, OrderDetails
import datetime 

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')
    context = {
        "user": request.user,
        "regular_pizza": Product.objects.filter(category=1),
        "s_pizza": Product.objects.filter(category=2),
        "subs": Product.objects.filter(category=3),
        "pasta": Product.objects.filter(category=4),
        "salad": Product.objects.filter(category=5),
        "dinner": Product.objects.filter(category=6)
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

def cart(request):
    return render(request, 'shoppingcart.html')
    
def addToCart(request):
    if request.method == "POST" and request.is_ajax():
        try: 
            pid = request.POST['product_id']
            size = request.POST['size']
            name = Product.objects.get(pk=pid).category.name + " - " + Product.objects.get(pk=pid).name
            price = 0
            if size == "large" :
                price = Product.objects.get(pk=pid).LPrice
            else:
                price = Product.objects.get(pk=pid).SPrice

            print(request.user)
            i = 0
            try:
                openOrder = OrderMain.objects.filter(userid = request.user)
                i= openOrder.id
            except (OrderMain.DoesNotExist):
                openOrder = OrderMain(userid = request.user, status = "open", total = price, createdDate= datetime.date.today())
                openOrder.save()
                openOrder = OrderMain.objects.filter(userid = request.user)
                i= openOrder.id
             
            od = OrderDetails(orderid = i, productid = pid, toppings="", price = price, size= size, productName= name, total = price, quantity = 1)
            od.save()

            return JsonResponse({"message": "Successfully added to cart!", "name":name, "price":price, "size": size, "total":""}, status=200)
        except Exception as err:
            print(err)
            return JsonResponse({"message": err}, status=400)
    size =request.POST['size']

   
