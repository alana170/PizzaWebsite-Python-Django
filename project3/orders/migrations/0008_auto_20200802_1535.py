# Generated by Django 3.0.8 on 2020-08-02 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_product_toppings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='price',
            field=models.FloatField(),
        ),
    ]
