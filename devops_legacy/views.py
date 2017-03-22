import os
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone


def overview(request):

    args = {
        'GERRIT_HOST': os.getenv('DEVOPS_PORTAL_GERRIT_HOST', 'localhost'),
        'GERRIT_PORT': os.getenv('DEVOPS_PORTAL_GERRIT_PORT', '8080'),
        'JENKINS_HOST': os.getenv('DEVOPS_PORTAL_JENKINS_HOST', 'localhost'),
        'JENKINS_PORT': os.getenv('DEVOPS_PORTAL_JENKINS_PORT', '8081'),
        'MAAS_HOST': os.getenv('DEVOPS_PORTAL_MAAS_HOST', 'localhost'),
        'MAAS_PORT': os.getenv('DEVOPS_PORTAL_MAAS_PORT', '80'),
        'ARTIFACTORY_HOST': os.getenv('DEVOPS_PORTAL_ARTIFACTORY_HOST', 'localhost'),
        'ARTIFACTORY_PORT': os.getenv('DEVOPS_PORTAL_ARTIFACTORY_PORT', '8082'),
    }

    return render(request, 'devops_portal/overview.html', args)


def jenkins(request):

    args = {
        'JENKINS_HOST': os.getenv('DEVOPS_PORTAL_JENKINS_HOST', 'localhost'),
        'JENKINS_PORT': os.getenv('DEVOPS_PORTAL_JENKINS_PORT', '8080'),
    }

    return render(request, 'devops_portal/jenkins.html', args)


def gerrit(request):
    args = {
        'GERRIT_HOST': os.getenv('DEVOPS_PORTAL_GERRIT_HOST', 'localhost'),
        'GERRIT_PORT': os.getenv('DEVOPS_PORTAL_GERRIT_PORT', '8080'),
    }

    return render(request, 'devops_portal/gerrit.html', args)


def maas(request):
    args = {
        'MAAS_HOST': os.getenv('DEVOPS_PORTAL_MAAS_HOST', 'localhost'),
        'MAAS_PORT': os.getenv('DEVOPS_PORTAL_MAAS_PORT', '80'),
    }

    return render(request, 'devops_portal/maas.html', args)


def artifactory(request):
    args = {
        'ARTIFACTORY_HOST': os.getenv('DEVOPS_PORTAL_ARTIFACTORY_HOST', 'localhost'),
        'ARTIFACTORY_PORT': os.getenv('DEVOPS_PORTAL_ARTIFACTORY_PORT', '8082'),
    }

    return render(request, 'devops_portal/artifactory.html', args)


def salt(request):
    args = {}

    return render(request, 'devops_portal/salt.html', args)


def doc(request):
    args = {}

    return render(request, 'devops_portal/doc.html', args)


def userguides(request):
    args = {}

    return render(request, 'devops_portal/userguides.html', args)
