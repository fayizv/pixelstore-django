# Generated by Django 4.0.6 on 2022-08-09 04:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_prodect_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='prodect_name',
            new_name='product_name',
        ),
    ]
