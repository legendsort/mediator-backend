# Generated by Django 4.0.3 on 2022-04-27 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0016_delete_upload'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesstype',
            name='codename',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
