from django.conf.urls import patterns
from django.conf.urls import url
from model_manager.dashboards.delivery.salt_control import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
)
