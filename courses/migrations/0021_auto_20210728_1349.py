# Generated by Django 3.1.1 on 2021-07-28 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0020_main_courses_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battleship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battleships', to='courses.contest')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battleships', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='BattleshipTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('battleship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battleship_teams', to='courses.battleship')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battleship_teams', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='BattleshipShip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('battleship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ships', to='courses.battleship')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ships', to='courses.battleshipteam')),
            ],
        ),
        migrations.AddField(
            model_name='participant',
            name='battleship_teams',
            field=models.ManyToManyField(blank=True, related_name='participants', to='courses.BattleshipTeam'),
        ),
    ]
