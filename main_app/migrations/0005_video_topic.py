# Generated by Django 4.1.5 on 2023-07-09 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_alter_course_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='topic',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
