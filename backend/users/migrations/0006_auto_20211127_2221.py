# Generated by Django 3.0.5 on 2021-11-27 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20211127_2200'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username',), 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
