from django.conf.urls import patterns
from django.conf.urls import url

from . import views

urlpatterns = patterns(
    '',
    url(r'^cookiecutter/create$',
        views.CreateView.as_view(), name='create'),
    url(r'^index$',
        views.IndexView.as_view(), name='index'),
)
