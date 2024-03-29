# Generated by Django 3.1.1 on 2021-08-09 18:01

import courses.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_battleship_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormBuilder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(unique=True)),
                ('title', models.TextField()),
                ('subtitle', models.TextField(blank=True)),
                ('send_mail', models.BooleanField(default=False)),
                ('mail_host', models.TextField(blank=True)),
                ('mail_port', models.TextField(blank=True)),
                ('mail_username', models.TextField(blank=True)),
                ('mail_password', models.TextField(blank=True)),
                ('mail_template', models.TextField(blank=True)),
                ('registerNameTemplate', models.TextField(blank=True)),
                ('registerApi', models.ManyToManyField(blank=True, related_name='forms', to='courses.EjudgeRegisterApi')),
            ],
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField()),
                ('type', models.CharField(choices=[('ST', 'Small text field'), ('IN', 'Number'), ('ML', 'Mail address'), ('PH', 'Phone number'), ('LO', 'Large text field'), ('CB', 'Check box'), ('TX', 'Some text')], default='ST', max_length=2)),
                ('required', models.BooleanField(default=False)),
                ('internal_name', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='courses.formbuilder')),
            ],
            bases=(models.Model, courses.models.FormFieldType),
        ),
        migrations.CreateModel(
            name='FormEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enteries', to='courses.formbuilder')),
            ],
        ),
    ]
