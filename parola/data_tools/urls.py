from django.conf.urls import url

from . import views

app_name = 'data_tools'
urlpatterns = [
    url(r'^cpc_extractor/', views.cpc_extractor, name='cpc_extractor'),
    url(r'^co_occurrence/', views.co_occurrence, name='co_occurrence'),
    url(r'^new_category_set_keywords/', views.new_category_set_keywords, name='new_category_set_keywords'),
    url(r'^categorize_by_keywords/(?P<data_set>.*)/(?P<category_set>.*)/$', views.categorize_by_keywords, name='categorize_by_keywords'),
    url(r'^view_category_sets/', views.view_category_sets, name='view_category_sets'),
    url(r'^view_training_sets/', views.view_training_sets, name='view_training_sets'),
    url(r'^new_training_setup/', views.new_training_setup, name='new_training_setup'),
    url(r'^view/(?P<training_set>.*)/$', views.view_training_set, name='view_training_set'),
    url(r'^automated_patent_classification/(?P<data_set>.*)/(?P<training_set>.*)/$', views.automated_patent_classification, name='automated_patent_classification'),
    url(r'^input_classification_bar_graph/', views.input_classification_bar_graph, name='input_classification_bar_graph'),
    url(r'^input_classification_accuracy_bar_graph/', views.input_classification_accuracy_bar_graph, name='input_classification_accuracy_bar_graph'),
    url(r'^download_sample_cpc_extractor/', views.download_sample_cpc_extractor, name='download_sample_cpc_extractor'),
    url(r'^download_sample_co_occurrence/', views.download_sample_co_occurrence, name='download_sample_co_occurrence'),
    url(r'^download_cpc_extractor/', views.download_cpc_extractor, name='download_cpc_extractor'),
    url(r'^download_co_occurrence/', views.download_co_occurrence, name='download_co_occurrence'),
    url(r'^download_sample_category_keywords/', views.download_sample_category_keywords, name='download_sample_category_keywords'),
    url(r'^download_categorize_by_keywords/', views.download_categorize_by_keywords, name='download_categorize_by_keywords'),
    url(r'^download_classification/', views.download_classification, name='download_classification'),
    url(r'^download_tag_words/', views.download_tag_words, name='download_tag_words'),
]