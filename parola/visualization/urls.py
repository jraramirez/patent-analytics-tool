from django.conf.urls import url

from . import views

app_name = 'visualization'
urlpatterns = [
    # url(r'^dataset_statistics/(?P<data_set>.*)/(?P<classification>.*)/$', views.dataset_statistics, name='dataset_statistics'),
    # url(r'^category_statistics/(?P<data_set>.*)/(?P<classification>.*)/(?P<category>.*)/$', views.category_statistics),
    # url(r'^assignee_statistics/(?P<data_set>.*)/(?P<classification>.*)/(?P<assignee>.*)/$', views.assignee_statistics),
    # url(r'^cluster_map/(?P<data_set>.*)/(?P<classification1>.*)/(?P<classification2>.*)/$', views.cluster_map, name='cluster_map'),
    # url(r'^landscape_map/(?P<data_set>.*)/$', views.landscape_map, name='landscape_map'),
]