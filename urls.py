from django.conf.urls import patterns, url
from django.views.generic import ListView

from permission import views
from permission.models import Publisher
from modules.alpha_pages import NamePaginator

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^publisher/$', views.publisher_index, name='publisher_index'),
	url(r'^publisher/(?P<publisher_id>\d+)/$', views.publisher_detail, name='publisher_detail'),
	url(r'^search/$', views.search, name='search'),
	url(r'^(?P<journal_id>\d+)/$', views.detail, name='detail'),
)

