# Generated by Django 4.0.3 on 2022-04-20 06:07

import Paper.helper
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Paper', '0017_remove_journal_frequency_journal_frequency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='categories',
            field=models.ManyToManyField(blank=True, through='Paper.JournalCategory', to='Paper.category'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='countries',
            field=models.ManyToManyField(blank=True, through='Paper.JournalCountry', to='Paper.country'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='guide_url',
            field=models.FileField(null=True, upload_to=Paper.helper.journal_resource_path),
        ),
        migrations.AlterField(
            model_name='journal',
            name='logo_url',
            field=models.ImageField(null=True, upload_to=Paper.helper.journal_resource_path),
        ),
        migrations.AlterField(
            model_name='journal',
            name='products',
            field=models.ManyToManyField(blank=True, through='Paper.JournalProductType', to='Paper.producttype'),
        ),
    ]