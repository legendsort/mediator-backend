# Generated by Django 4.0.4 on 2022-07-27 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Paper', '0048_exchange'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchange',
            name='site_url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
