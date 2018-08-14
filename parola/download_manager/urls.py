from django.conf.urls import url

from . import views

app_name = 'download_manager'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^download_chart_raw_data/(?P<app_name>.*)/(?P<file_name>.*)/(?P<file_type>.*)/$', views.download_chart_raw_data, name='download_chart_raw_data'),
]