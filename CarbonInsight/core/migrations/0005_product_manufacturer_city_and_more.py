# Generated by Django 5.2 on 2025-05-16 11:22

import django.core.validators
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_manufacturer_product_manufacturer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='manufacturer_city',
            field=models.CharField(default='Eindhoven', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer_country',
            field=django_countries.fields.CountryField(default='NL', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer_street',
            field=models.CharField(default='De Zaale', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer_zip_code',
            field=models.CharField(default='5612XX', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='year_of_construction',
            field=models.IntegerField(default=1971, validators=[django.core.validators.MinValueValidator(1900)]),
            preserve_default=False,
        ),
    ]
