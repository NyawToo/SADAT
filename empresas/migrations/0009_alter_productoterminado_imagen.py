# Generated by Django 4.2.7 on 2025-04-14 19:22

from django.db import migrations, models
import empresas.models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0008_alter_microempresaintegral_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productoterminado',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to=empresas.models.ProductoTerminado.get_upload_path),
        ),
    ]
