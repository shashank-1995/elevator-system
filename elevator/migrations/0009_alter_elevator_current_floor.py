# Generated by Django 4.2.4 on 2023-08-06 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elevator', '0008_elevator_direction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elevator',
            name='current_floor',
            field=models.IntegerField(default=0),
        ),
    ]
