# Generated by Django 4.0.4 on 2022-07-27 14:49

import Paper.helper
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Paper', '0047_alter_order_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_upload', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('purpose', models.CharField(max_length=255, null=True)),
                ('additional_info', models.JSONField(null=True)),
                ('detail', models.TextField(null=True)),
                ('attachment', models.FileField(max_length=1024, null=True, upload_to=Paper.helper.exchange_attachment_path)),
                ('dealer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='exchange_dealer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
