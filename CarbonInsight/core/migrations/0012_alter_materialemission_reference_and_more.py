# Generated by Django 5.2 on 2025-05-22 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_emission_pcf_calculation_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialemission',
            name='reference',
            field=models.ForeignKey(blank=True, help_text='Reference values for the material emission', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='material_emissions', to='core.materialemissionreference'),
        ),
        migrations.AlterField(
            model_name='productionenergyemission',
            name='reference',
            field=models.ForeignKey(blank=True, help_text='Reference values for the production energy emission', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='production_emissions', to='core.productionenergyemissionreference'),
        ),
        migrations.AlterField(
            model_name='transportemission',
            name='reference',
            field=models.ForeignKey(blank=True, help_text='Reference values for the transport emission', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transport_emissions', to='core.transportemissionreference'),
        ),
        migrations.AlterField(
            model_name='userenergyemission',
            name='reference',
            field=models.ForeignKey(blank=True, help_text='Reference values for the user energy emission', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_emissions', to='core.userenergyemissionreference'),
        ),
    ]
