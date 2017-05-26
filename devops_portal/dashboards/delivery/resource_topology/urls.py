from django.conf.urls import patterns
from django.conf.urls import url
from devops_portal.dashboards.delivery.resource_topology import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^topology_data', views.topology_data_view, name='status')
)
