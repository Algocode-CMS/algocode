from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0068_formaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='level',
            field=models.CharField(
                blank=True,
                choices=[('basic', 'Основной'), ('advanced', 'Продвинутый')],
                default='',
                max_length=20,
                verbose_name='Уровень',
            ),
        ),
        migrations.AddField(
            model_name='contest',
            name='track',
            field=models.CharField(
                blank=True,
                choices=[('math', 'Математика'), ('ml', 'ML')],
                default='',
                max_length=20,
                verbose_name='Трек',
            ),
        ),
    ]
