# Generated by Django 4.0.3 on 2022-04-27 02:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0017_businesstype_codename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_type', to='Account.businesstype'),
        ),
        migrations.AlterField(
            model_name='remoteaccount',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_account_business', to='Account.businesstype'),
        ),
        migrations.AlterField(
            model_name='remoteaccount',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_remote_account', to=settings.AUTH_USER_MODEL),
        ),
    ]