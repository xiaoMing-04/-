# Generated by Django 5.0 on 2025-04-12 23:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_rename_title_game_name_remove_game_image_url_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='quantity',
        ),
        migrations.AlterField(
            model_name='game',
            name='discount',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
