# Generated by Django 4.2.10 on 2024-10-17 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0065_contest_enable_start_time_contest_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]