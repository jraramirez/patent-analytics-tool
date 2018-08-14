from django.conf.urls import url

from . import views
from data_sets import views as data_sets_views
from uspto import views as uspto_views
from data_tools import views as data_tools_views
from parola_refine import views as parola_refine_views
from visualization import views as visualization_tools_views

app_name = 'main'
urlpatterns = [
    url(r'', views.index, name='index'),
    # url(r'^data_sets/new_data_setup', data_sets_views.new_data_setup, name='new_data_setup'),
    # url(r'^data_sets/view_data_sets', data_sets_views.view_data_sets, name='view_data_sets'),

    # url(r'^view_category_sets/(?P<category_set>.*)/$', data_tools_views.view_category_sets, name='view_category_sets'),
    # url(r'^new_category_set_keywords/', data_tools_views.new_category_set_keywords, name='new_category_set_keywords'),
    # url(r'^categorize_by_keywords/(?P<data_set>.*)/(?P<category_set>.*)/$', data_tools_views.categorize_by_keywords, name='categorize_by_keywords'),
    # url(r'^new_training_setup/', data_tools_views.new_training_setup, name='new_training_setup'),
    # url(r'^view/(?P<training_set>.*)/$', data_tools_views.view_training_set, name='view_training_set'),
    # url(r'^automated_patent_classification/(?P<data_set>.*)/(?P<training_set>.*)/$', data_tools_views.automated_patent_classification, name='automated_patent_classification'),
    # url(r'^reference_update', parola_refine_views.reference_update, name='reference_update'),
    # url(r'^assignee_grouping/(?P<data_set>.*)/$', parola_refine_views.assignee_grouping, name='assignee_grouping'),

    # url(r'^dataset_statistics/(?P<data_set>.*)/(?P<classification>.*)/$', visualization_tools_views.dataset_statistics, name='dataset_statistics'),
    # url(r'^category_statistics/(?P<data_set>.*)/(?P<classification>.*)/(?P<category>.*)/$', visualization_tools_views.category_statistics),
    # url(r'^assignee_statistics/(?P<data_set>.*)/(?P<classification>.*)/(?P<assignee>.*)/$', visualization_tools_views.assignee_statistics),
    # url(r'^cluster_map/(?P<data_set>.*)/(?P<classification1>.*)/(?P<classification2>.*)/$', visualization_tools_views.cluster_map, name='cluster_map'),
    # url(r'^landscape_map/(?P<data_set>.*)/$', visualization_tools_views.landscape_map, name='landscape_map'),
]