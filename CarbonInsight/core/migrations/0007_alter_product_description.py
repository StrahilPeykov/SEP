# Generated by Django 5.2 on 2025-05-16 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_product_family'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default='Product description'),
            preserve_default=False,
        ),
    ]
