

from devops_portal_backend.views import *
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from .authtoken.views import obtain_auth_token

urlpatterns = patterns('',

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^doc/', include('django.contrib.admindocs.urls')),

                       url(r'^api/', include('devops_portal_backend.router')),
                       url(r'^api/auth/', obtain_auth_token),

                       )

urlpatterns += patterns('',
                        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                            'document_root': settings.MEDIA_ROOT}))

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                            'document_root': settings.STATIC_ROOT}))
