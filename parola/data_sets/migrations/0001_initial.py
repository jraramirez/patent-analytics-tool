# Generated by Django 2.0 on 2018-04-04 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Datasets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'datasets',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Patents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_number', models.CharField(blank=True, max_length=45, null=True)),
                ('publication_numbers', models.CharField(blank=True, max_length=45, null=True)),
                ('year', models.CharField(blank=True, max_length=45, null=True)),
                ('titles', models.CharField(blank=True, max_length=1000, null=True)),
                ('abstracts', models.CharField(blank=True, max_length=1000, null=True)),
                ('independent_claims', models.CharField(blank=True, max_length=1000, null=True)),
                ('cpc', models.CharField(blank=True, max_length=1000, null=True)),
                ('main_cpc', models.CharField(blank=True, max_length=45, null=True)),
                ('category', models.CharField(blank=True, max_length=300, null=True)),
                ('market_segment', models.CharField(blank=True, max_length=45, null=True)),
                ('current_assignee', models.CharField(blank=True, max_length=300, null=True)),
                ('original_assignee', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'db_table': 'patents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DatasetPatent',
            fields=[
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='data_sets.Datasets')),
            ],
            options={
                'db_table': 'dataset_patent',
                'managed': False,
            },
        ),
    ]
