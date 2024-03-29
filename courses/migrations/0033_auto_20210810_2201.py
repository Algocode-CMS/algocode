# Generated by Django 3.1.1 on 2021-08-10 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0032_auto_20210810_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='type',
            field=models.CharField(choices=[('ST', 'Small text field'), ('IN', 'Number'), ('ML', 'Mail address'), ('PH', 'Phone number'), ('DT', 'Date'), ('LO', 'Large textarea'), ('CB', 'Check box'), ('TX', 'Text without field')], default='ST', max_length=2),
        ),
    ]
