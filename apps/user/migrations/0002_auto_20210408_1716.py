# Generated by Django 3.1.7 on 2021-04-08 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='address',
            table='my_address',
        ),
        migrations.AlterModelTable(
            name='user',
            table='my_user',
        ),
    ]
