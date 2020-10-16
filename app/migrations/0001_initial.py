# Generated by Django 3.1.2 on 2020-10-16 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_unaccent', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_unaccent', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255, unique=True)),
                ('actors', models.ManyToManyField(to='app.Actor')),
            ],
        ),
    ]
