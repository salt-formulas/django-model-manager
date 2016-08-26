from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^overview$', views.overview, name='overview'),
    url(r'^jenkins/$', views.jenkins, name='jenkins'),
    url(r'^gerrit/$', views.gerrit, name='gerrit'),
    url(r'^maas/$', views.maas, name='maas'),
    url(r'^artifactory/$', views.artifactory, name='artifactory'),
    url(r'^salt/$', views.salt, name='salt'),
    url(r'^doc/$', views.doc, name='doc'),
)
