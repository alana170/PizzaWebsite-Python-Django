from django.contrib import admin
from .models import ProductCategory, Product, OrderDetails, OrderMain

  # Register your models here.
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(OrderMain)
admin.site.register(OrderDetails)