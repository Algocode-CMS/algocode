# Generated by Django 3.2.6 on 2023-06-28 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0058_formsheetsexport'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='contests_text',
            field=models.TextField(default='Занятия'),
        ),
    ]
