from django.conf.urls import url

from . import views

app_name = 'parola_refine'
urlpatterns = [
    url(r'^reference_update', views.reference_update, name='reference_update'),
    url(r'^assignee_grouping/(?P<data_set>.*)/$', views.assignee_grouping, name='assignee_grouping'),
]