# Generated by Django 2.2.dev20190108192533 on 2019-01-09 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hearthstone', '0002_auto_20190108_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='elo',
            field=models.IntegerField(default=1000),
        ),
    ]