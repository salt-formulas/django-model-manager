
from __future__ import absolute_import

import logging

from django.utils import six
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from .models import *
from .serializers import *

LOG = logging.getLogger(__name__)


class BaseViewSet(viewsets.ModelViewSet):

    """use specific serializer for actions
    """

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'closed']:
            return getattr(self,
                           "serializer_class_list",
                           self.serializer_class)
        if self.action == "create":
            return getattr(self,
                           "serializer_class_create",
                           self.serializer_class)
        return self.serializer_class

    @property
    def ready_queryset(self):
        '''returns user ready queryset'''
        queryset = self.queryset

        if not self.request.user.is_operator:
            # filter only user tickets
            queryset = queryset.filter(
                organisation=self.request.user.organisation.pk)
        elif self.request.user.is_operator:
            # filter operator tickets
            queryset = queryset.filter(
                organisation__pk__in=self.request.user.manage_organisations)
        return queryset


class UserViewSet(BaseViewSet):

    serializer_class = UserSerializer
    serializer_class_create = UserSerializerCreate
    queryset = User.objects.all()
    filter_fields = ('operator', 'organisation')

    @detail_route(methods=['post'])
    def set_password(self, request, pk=None):
        # for future we must get actual password and authorize this user !!
        user = self.get_object()
        user.set_password(request.data['new_password'])
        user.save()
        return Response({'status': 'password set'})


class OrganisationView(BaseViewSet):

    serializer_class = OrganisationSerializer
    queryset = Organisation.objects.all()

    @detail_route(methods=['get'])
    def summary(self, request, pk):
        """return organisation summary
        """
        organisation = self.get_object()
        return Response(organisation.summary)

