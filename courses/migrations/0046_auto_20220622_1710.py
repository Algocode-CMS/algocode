# Generated by Django 3.2.6 on 2022-06-22 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0045_polechudesteam_coins'),
    ]

    operations = [
        migrations.AddField(
            model_name='polechudesteam',
            name='unsuccess',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='polechudesteam',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
