from django.db import models

# Create your models here.
class ProductCategory(models.Model): 
    name= models.CharField(max_length=90)
    
    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    name= models.CharField(max_length=90)
    category= models.ForeignKey(ProductCategory,on_delete=models.CASCADE,related_name="category")
    SPrice= models.DecimalField(max_digits=6, decimal_places=2)
    LPrice= models.DecimalField(max_digits=6, decimal_places=2)
    toppings = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"


class OrderMaster(models.Model):
    userid = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    createdDate = models.DateField()

    def __str__(self):
        return f"{self.userid} - Status: {self.status} Total: {self.total}"

class OrderDetail(models.Model):
    orderid = models.ForeignKey(OrderMaster, on_delete=models.CASCADE, related_name ="order_id")
    productid = models.IntegerField()
    toppings = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.CharField(max_length=50)
    productName = models.CharField(max_length=90)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.productName} - Total: {self.total} Toppings: {self.toppings}"