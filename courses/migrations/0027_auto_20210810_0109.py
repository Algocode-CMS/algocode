# Generated by Django 3.1.1 on 2021-08-09 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_auto_20210810_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='formentry',
            name='ip',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='formentry',
            name='mail',
            field=models.TextField(blank=True),
        ),
    ]
