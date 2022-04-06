# Generated by Django 4.0.3 on 2022-04-12 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Paper', '0009_journalcountry_journalfrequency_journal_countries_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='JournalProductType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('journal', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='journal_product', to='Paper.journal')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_journal', to='Paper.producttype')),
            ],
        ),
        migrations.AddField(
            model_name='journal',
            name='products',
            field=models.ManyToManyField(blank=True, through='Paper.JournalProductType', to='Paper.producttype'),
        ),
    ]
