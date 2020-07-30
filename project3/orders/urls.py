from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup"),
    path("login", views.signin, name="login"),
    path("cart", views.cart, name="cart")
]
