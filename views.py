from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone


def overview(request):
    args = {}

    return render(request, 'devops-portal/overview.html', args)


def jenkins(request):
    args = {}

    return render(request, 'devops-portal/jenkins.html', args)


def gerrit(request):
    args = {}

    return render(request, 'devops-portal/gerrit.html', args)


def maas(request):
    args = {}

    return render(request, 'devops-portal/maas.html', args)


def artifactory(request):
    args = {}

    return render(request, 'devops-portal/artifactory.html', args)


def salt(request):
    args = {}

    return render(request, 'devops-portal/salt.html', args)


def doc(request):
    args = {}

    return render(request, 'devops-portal/doc.html', args)
