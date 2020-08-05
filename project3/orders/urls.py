from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup"),
    path("login", views.signin, name="login"),
    path("cart", views.ordered, name="cart"),
    path("addCart", views.addToCart, name="addCart"),
    path("logout", views.logout_view, name="logout"),
    path("deleteItem", views.delete_item, name="deleteItem"),
    path("placeOrder", views.ordered, name="placeOrder"),
    path("clearCart", views.clearCart, name="clearCart"),
]
