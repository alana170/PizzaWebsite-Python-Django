from django.db import models

# Create your models here.
class ProductCategory(models.Model): 
    name= models.CharField(max_length=90)
    
    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    name= models.CharField(max_length=90)
    category= models.ForeignKey(ProductCategory,on_delete=models.CASCADE,related_name="category")
    SPrice= models.FloatField()
    LPrice= models.FloatField()
    toppings= models.IntegerField()

    def __str__(self):
        return f"{self.name}  Small: {self.SPrice} Large: {self.LPrice}"