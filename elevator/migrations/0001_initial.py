# Generated by Django 4.2.4 on 2023-08-04 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Elevator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('current_floor', models.PositiveIntegerField()),
                ('is_moving', models.BooleanField(default=False)),
                ('is_operational', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('number', models.PositiveIntegerField(unique=True)),
                ('direction', models.CharField(choices=[('UP', 'Up'), ('DOWN', 'Down')], max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(choices=[('UP', 'Up'), ('DOWN', 'Down')], max_length=10)),
                ('elevator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elevator.elevator')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elevator.floor')),
            ],
        ),
    ]
