# Generated by Django 2.2.dev20190111110410 on 2019-01-11 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hearthstone', '0009_auto_20190111_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='card1',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='exchange_card1', to='hearthstone.Card'),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_status',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='user1_status',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='user2_status',
            field=models.IntegerField(blank=True),
        ),
    ]
