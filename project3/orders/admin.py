from django.contrib import admin
from .models import ProductCategory, Product, OrderDetail, OrderMaster

  # Register your models here.
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(OrderMaster)
admin.site.register(OrderDetail)