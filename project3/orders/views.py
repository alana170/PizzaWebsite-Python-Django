from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from . import views 
from django.contrib.auth.models import User
from orders.models import Product, ProductCategory, OrderMaster, OrderDetail
import datetime 
from decimal import Decimal

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')
    
    openOrder = OrderMaster.objects.filter(userid = request.user, status="open").first() 
    items = None
    total = 0.0
    if openOrder is not None: 
        items = OrderDetail.objects.filter(orderid = openOrder)
        total = openOrder.total
    context = {
        "user": request.user,
        "regular_pizza": Product.objects.filter(category=1),
        "s_pizza": Product.objects.filter(category=2),
        "subs": Product.objects.filter(category=3),
        "pasta": Product.objects.filter(category=4),
        "salad": Product.objects.filter(category=5),
        "dinner": Product.objects.filter(category=6),
        "items": items,
        "total" : total,
        "toppings": Product.objects.filter(category=7)
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {"message": "Invalid credentials."})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return render(request, "login.html", {"message": "Logged out."})

def cart(request):
    return render(request, 'cartsummary.html')
    
def addToCart(request):
    if request.method == "POST" and request.is_ajax():
        try: 
            pid = request.POST['product_id']
            size = request.POST['size']
            toppings = request.POST['toppings']
            print("toppings = " + toppings)
            name = Product.objects.get(pk=pid).category.name + " - " + Product.objects.get(pk=pid).name
            price = 0.0
            if size == "large" :
                price = Product.objects.get(pk=pid).LPrice
            else:
                price = Product.objects.get(pk=pid).SPrice

            
            try:
                openOrder = OrderMaster.objects.filter(userid = request.user, status ="open").first() 
                if openOrder is None : 
                    openOrder = OrderMaster(userid = request.user, status = "open", total = price, createdDate= datetime.date.today())
                    openOrder.save()
            except OrderMaster.DoesNotExist:
                openOrder = OrderMaster(userid = request.user, status = "open", total = price, createdDate= datetime.date.today())
                openOrder.save()
            except ValueError as err:
                print(err)
               
            openOrder = OrderMaster.objects.filter(userid = request.user, status="open").first() 
              
            od = OrderDetail(orderid = openOrder, productid = pid, toppings=toppings, price = price, size= size, productName= name, total = price, quantity = 1)
            od.save() 
            odid = od.id
            queryset = OrderDetail.objects.filter(orderid = openOrder)
            total = 0
            for item in queryset:
                total = item.price + total

            openOrder.total = total
            openOrder.save()
            return JsonResponse({"message": "Successfully added to cart!", "name":name, "price":price, "size": size, "total": total, "id" : odid}, status=200)
        
        except Exception as err:
            print(err)
            return JsonResponse({"message": err}, status=400)
        
def delete_item(request) :
    if request.method == "POST" and request.is_ajax():
        try: 
            id = request.POST['id']
            orderItem = OrderDetail.objects.get(pk =id)
            price = orderItem.price
            om = orderItem.orderid
            om.total = om.total - price
            total = om.total
            om.save()
            if orderItem.total <= 0 :
                total = 0.00
            orderItem.delete()
            
            return JsonResponse({"message": "Successfully deleted from cart!", "total": total}, status=200)
        
        except Exception as err:
            print(err)
            return JsonResponse({"message": err}, status=400)


def clearCart(request) :
    if request.method == "POST" and request.is_ajax():
        try: 
            openOrder = OrderMaster.objects.filter(userid = request.user, status="open").first() 
            openOrder.status = "deleted"
            openOrder.save()

            return JsonResponse({"message": "Successfully cleared all from cart!"}, status=200)
        
        except Exception as err:
            print(err)
            return JsonResponse({"message": err}, status=400)    


def ordered(request) : 
    items = None
    total = 0
    message = ""

    if request.method=="POST" and request.is_ajax():
        openOrder = OrderMaster.objects.filter(userid = request.user, status="open").first() 
        if openOrder is not None:
            openOrder.status = "in progress"
            openOrder.save()
            message = "Order is in progress..."
            
    else:
        openOrder = OrderMaster.objects.filter(userid = request.user, status="open").first() 
        
        if openOrder is not None: 
            items = OrderDetail.objects.filter(orderid = openOrder)
            total = openOrder.total
        else:
            message = "You have no items in your cart. Please go back and add some!"

    context = {
        "items" : items,
        "message": message,
        "total" : total
    }
    return render(request, "cartsummary.html", context)