# Generated by Django 5.1.4 on 2025-02-04 06:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_alter_comment_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='default_image_index',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)]),
        ),
    ]
