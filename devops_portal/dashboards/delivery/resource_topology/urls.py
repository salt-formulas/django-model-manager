from django.conf.urls import patterns
from django.conf.urls import url
from devops_portal.dashboards.delivery.resource_topology import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^topology_data/(?P<domain>[\w\.\-]+)$', views.topology_data_view, name='topology_data'),
    url(r'^topology_data/(?P<domain>[\w\.\-]+)/(?P<chart_node>[\w\.\-]+)$', views.pillar_data_view, name='pillar_data'),
    url(r'^(?P<domain>[\w\.\-]+)$', views.DetailView.as_view(), name='detail')
)
