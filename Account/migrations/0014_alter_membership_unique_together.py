# Generated by Django 4.0.3 on 2022-04-22 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0013_user_created_at_user_updated_at'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together={('role', 'permission')},
        ),
    ]
