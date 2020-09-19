# Generated by Django 3.1.1 on 2020-09-19 20:00

from django.db import migrations, models
import django.db.models.deletion


def add_course_teacher(apps, schema_editor):
    Teacher = apps.get_model('courses', 'Teacher')
    TeacherInCourse = apps.get_model('courses', 'TeacherInCourse')
    for teacher in Teacher.objects.all():
        for course in teacher.courses.all():
            TeacherInCourse.objects.create(course=course, teacher=teacher, note="", priority=0)


def revert_course_teacher(apps, schema_editor):
    TeacherInCourse = apps.get_model('courses', 'TeacherInCourse')
    for teacher_in_course in TeacherInCourse.objects.all():
        teacher_in_course.course.teachers.add(teacher_in_course.teacher)


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_auto_20200906_1954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='name_in_main',
        ),
        migrations.RemoveField(
            model_name='course',
            name='url',
        ),
        migrations.CreateModel(
            name='TeacherInCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_teachers', to='courses.course')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_courses', to='courses.teacher')),
            ],
        ),
        migrations.RunPython(add_course_teacher, revert_course_teacher),
        migrations.RemoveField(
            model_name='course',
            name='teachers',
        ),
    ]
