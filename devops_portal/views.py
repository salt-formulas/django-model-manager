from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone


def overview(request):
    args = {}

    return render(request, 'devops_portal/overview.html', args)


def jenkins(request):
    args = {}

    return render(request, 'devops_portal/jenkins.html', args)


def gerrit(request):
    args = {}

    return render(request, 'devops_portal/gerrit.html', args)


def maas(request):
    args = {}

    return render(request, 'devops_portal/maas.html', args)


def artifactory(request):
    args = {}

    return render(request, 'devops_portal/artifactory.html', args)


def salt(request):
    args = {}

    return render(request, 'devops_portal/salt.html', args)


def doc(request):
    args = {}

    return render(request, 'devops_portal/doc.html', args)
