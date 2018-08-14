from django.db import models

class Patents(models.Model):
    application_number = models.CharField(max_length=45, blank=True, null=True)
    publication_numbers = models.CharField(max_length=45, blank=True, null=True)
    year = models.CharField(max_length=45, blank=True, null=True)
    titles = models.CharField(max_length=1000, blank=True, null=True)
    absracts = models.CharField(max_length=1000, blank=True, null=True)
    independent_claims = models.CharField(max_length=1000, blank=True, null=True)
    cpc = models.CharField(max_length=1000, blank=True, null=True)
    main_cpc = models.CharField(max_length=45, blank=True, null=True)
    category = models.CharField(max_length=300, blank=True, null=True)
    market_segment = models.CharField(max_length=45, blank=True, null=True)
    current_assignee = models.CharField(max_length=300, blank=True, null=True)
    original_assignee = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'patents'

class Datasets(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datasets'

class DatasetPatent(models.Model):
    dataset = models.ForeignKey('Datasets', models.DO_NOTHING, primary_key=True)
    patent = models.ForeignKey('Patents', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dataset_patent'
        unique_together = (('dataset', 'patent'),)
