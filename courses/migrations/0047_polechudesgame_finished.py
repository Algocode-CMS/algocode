# Generated by Django 3.2.6 on 2022-06-23 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0046_auto_20220622_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='polechudesgame',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]
