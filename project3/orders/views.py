from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from . import views 
from django.contrib.auth.models import User
from orders.models import Product, ProductCategory, OrderMaster, OrderDetail
import datetime 
from decimal import Decimal
import stripe
import json
import os

stripe.api_key = 'sk_test_51HDKj6GM1nFLbkHBXr8jJ1IOSSHqadxmYNiYPNnmxPO3pA6I87bszcwdF03Wq69iCMUAV9eKI6QV4hDCu2m7GXpp00I147paoc'
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

def orderhistory(request): 
    progressOrders = None
    completedOrders = None
    cancelledOrders = None
    if request.method=="GET":
        progressOrders = OrderMaster.objects.filter(userid = request.user, status="in progress").order_by('-createdDate').all()
        completedOrders = OrderMaster.objects.filter(userid = request.user, status="completed").order_by('-createdDate').all()
        cancelledOrders = OrderMaster.objects.filter(userid = request.user, status="cancelled").order_by('-createdDate').all()

    context = {
        "pOrders" : progressOrders,
        "cOrders": completedOrders,
        "dOrders" : cancelledOrders,
    }
    return render(request, "orderhistory.html", context)

def orderdetails(request, id):
    order = OrderDetail.objects.filter(orderid = id).all()
    total = OrderMaster.objects.get(pk= id).total
    context = {
        "order" : order,
        "total" : total,
    }
    return render(request, "orderdetails.html", context)

def cancelOrder(request) :
    if request.method=="POST" and request.is_ajax():
        try:
            id = request.POST["id"]
            cancel_order = OrderMaster.objects.get(pk =id)
            cancel_order.status = "cancelled"
            cancel_order.save()
            return JsonResponse({"message": "Successfully cancelled order!"}, status=200)
        except Exception as err:
            print(err)
            return JsonResponse({"message": err}, status=400)    

def checkUser(request) : 
    if request.method=="POST" and request.is_ajax():
        try:
            username = request.POST["username"]
            if User.objects.get(username=username) is not None : 
                return JsonResponse({"message": "Username already exists."}, status=200)
            else: 
                return JsonResponse({"message" : "Username is not taken yet."}, status=200)

        except Exception as err:
            print(err)
            return JsonResponse({"message": err}, status=400)   

def checkout(request) :
    if request.method == "POST" and request.is_ajax():
        try: 
            total = OrderMaster.objects.filter(userid = request.user, status="open").first().total 
            u = request.user
            print(u)
            uobj = User.objects.filter(username=u).first()
            email = uobj.email
            name = uobj.first_name
            print(total)
            print(name+ " " + "  " + email+ " ")
        except Exception as err:
            print(err)
            return JsonResponse({"message" : "Unable to identify user. Login and try again."}, status=400)

        try:
            token = stripe.Token.create(
            card={
            "number": request.POST['cardNumber'],
            "exp_month": request.POST['exp_month'],
            "exp_year": request.POST['exp_year'],
            "cvc": request.POST['cvc'],
            },
            )

            customer = stripe.Customer.create(
            email = email,
            name = name,
            source= token.id,
            )
            #save stripe customer id, username, email in one model table - stripe customer info


            charge = stripe.Charge.create(
            amount=5000,
            currency="usd",
            source=token.id,
            description="Buying Pizza",
            )
            #save charge id, amount, date processed, Payments Model 
            

        except Exception as err:
            error = str(err)
            print(error)
            return JsonResponse({"message" :error }, status=400)
        
          
        return JsonResponse({"message" : "Payment submitted successfully."},status=200)
    return render(request, "checkout.html")

            