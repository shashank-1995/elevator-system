# Generated by Django 4.2.4 on 2023-08-06 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elevator', '0007_elevator_is_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='elevator',
            name='direction',
            field=models.CharField(choices=[('UP', 'Up'), ('DOWN', 'Down')], default='Up', max_length=10),
            preserve_default=False,
        ),
    ]
