from django.conf.urls import patterns
from django.conf.urls import url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^version/$', views.ContextVersionView.as_view(), name='version')
    # url(r'^(?P<build_id>[\w\.\-]+)/detail',
    #    views.DetailView.as_view(), name='detail'),
)
