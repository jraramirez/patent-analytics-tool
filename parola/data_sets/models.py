from django.db import models

class Datasets(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    source = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datasets'

class Patents(models.Model):
    application_number = models.CharField(max_length=45, blank=True, null=True)
    publication_numbers = models.TextField(blank=True, null=True)
    year = models.CharField(max_length=45, blank=True, null=True)
    titles = models.TextField(blank=True, null=True)
    abstracts = models.TextField(blank=True, null=True)
    independent_claims = models.TextField(blank=True, null=True)
    cpc = models.TextField(blank=True, null=True)
    main_cpc = models.CharField(max_length=45, blank=True, null=True)
    category = models.CharField(max_length=300, blank=True, null=True)
    market_segment = models.TextField(blank=True, null=True)
    current_assignee = models.TextField(blank=True, null=True)
    original_assignee = models.CharField(max_length=300, blank=True, null=True)
    dataset = models.ForeignKey(Datasets, models.DO_NOTHING, blank=True, null=True)
    predicted_categories = models.TextField(blank=True, null=True)
    predicted_market_segments = models.TextField(blank=True, null=True)
    predicted_topic = models.TextField(blank=True, null=True)
    main_cpc_description = models.TextField(blank=True, null=True)
    cpc_descriptions = models.TextField(blank=True, null=True)
    category_by_keywords = models.TextField(blank=True, null=True)
    technical_concepts = models.TextField(blank=True, null=True)
    category2 = models.TextField(blank=True, null=True)
    category3 = models.TextField(blank=True, null=True)
    category4 = models.TextField(blank=True, null=True)
    category5 = models.TextField(blank=True, null=True)
    category6 = models.TextField(blank=True, null=True)
    category7 = models.TextField(blank=True, null=True)
    patent_type = models.CharField(max_length=45, blank=True, null=True)
    clean_current_assignees = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'patents'

class RefCpcDescriptions(models.Model):
    cpc = models.CharField(max_length=45, blank=True, null=True)
    default_cpc = models.CharField(max_length=45, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ref_cpc_descriptions'

class RefCategoryKeywords(models.Model):
    group = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ref_category_keywords'
    
class RefAssigneeKeywords(models.Model):
    group = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ref_assignee_keywords'
    
class TrainingDatasets(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    classification = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'training_datasets'


class TrainingPatents(models.Model):
    titles = models.TextField(blank=True, null=True)
    abstracts = models.TextField(blank=True, null=True)
    independent_claims = models.TextField(blank=True, null=True)
    classification = models.TextField(blank=True, null=True)
    training_datasets = models.ForeignKey(TrainingDatasets, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'training_patents'

class CategorySet(models.Model):
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category_set'

class CategorySetKeywords(models.Model):
    category = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    category_set = models.ForeignKey(CategorySet, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'category_set_keywords'

class Assignees(models.Model):
    name = models.TextField(blank=True, null=True)
    group = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    sector = models.TextField(blank=True, null=True)
    industry = models.TextField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assignees'