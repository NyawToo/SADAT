# Generated by Django 4.2.7 on 2025-04-14 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='tipo',
            field=models.CharField(choices=[('integral', 'Microempresa Integral'), ('satelite', 'Microempresa Satélite'), ('cliente', 'Cliente'), ('superusuario', 'Super Usuario')], default='cliente', max_length=20),
        ),
    ]
