from __future__ import absolute_import

import xml.etree.ElementTree as ET

import jenkins
import json
import logging
import requests
import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import Request

LOG = logging.getLogger(__name__)

JOB_INFO = '%(folder_url)sjob/%(short_name)s/api/json?depth=%(depth)s'
# Requires Pipeline Stage View plugin
BUILD_WF = '%(folder_url)sjob/%(short_name)s/build'
BUILD_WITH_PARAMS_WF = '%(folder_url)sjob/%(short_name)s/buildWithParameters'
WF_NODE_LOG = '%(folder_url)sjob/%(short_name)s/%(number)d/execution/node/%(node)s/wfapi/log'
WF_BUILD_INFO = '%(folder_url)sjob/%(short_name)s/%(number)d/wfapi/describe'

JENKINS_CLIENT = None

if not JENKINS_CLIENT:

    try:
        jenkins_url = settings.JENKINS_API_URL
        jenkins_user = settings.JENKINS_API_USERNAME
        jenkins_pass = settings.JENKINS_API_PASSWORD
    except AttributeError as e:
        attr = e.message.split(' ')[-1]
        raise ImproperlyConfigured("The %s setting must not be empty." % attr)

    JENKINS_CLIENT = jenkins.Jenkins(
        jenkins_url,
        username=jenkins_user,
        password=jenkins_pass)


class JenkinsException(Exception):
    '''General exception type for jenkins-API-related failures.'''
    pass


class JenkinsClientExtension(object):

    """Base wrapper around jenkins api
    """

    def get_workflows(self):
        jobs = self.client.get_jobs()

        return jobs
        # filter(lambda job: "workflow" in job["name"], jobs)

    def get_builds(self, name):
        job_info = self.client.get_job_info(name)
        builds = job_info['builds']

        for build in builds:
            build_info = self.client.get_build_info(name, build['number'])
            build.update(build_info)
            build['job_name'] = name

        return builds

    def get_tree(self):
        works = self.get_workflows()
        for work in works:
            myConfig = self._client.get_job_config(work['name'])
            tree = ET.ElementTree(ET.fromstring(myConfig))
            root = tree.getroot()

            result = []

            for child in root:
                result += child.attrib

        return result

    def get_wf_build_info(self, name, number):
        '''Get build information dictionary. Requires Pipeline Stage View plugin.

        :param name: Job name, ``str``
        :param name: Build number, ``int``
        :returns: dictionary of build information, ``dict``
        '''
        folder_url, short_name = self.client._get_job_folder(name)
        try:
            response = self.client.jenkins_open(Request(
                self._build_url(WF_BUILD_INFO, locals())
            ))
            if response:
                return json.loads(response)
            else:
                raise jenkins.JenkinsException('job[%s] number[%d] does not exist'
                                               % (name, number))
        except HTTPError:
            raise jenkins.JenkinsException('job[%s] number[%d] does not exist'
                                           % (name, number))
        except ValueError:
            raise jenkins.JenkinsException(
                'Could not parse JSON info for job[%s] number[%d]'
                % (name, number)
            )

    def get_wf_node_log(self, name, number, node):
        '''Get build log for execution node. Requires Pipeline Stage View plugin.

        :param name: Job name, ``str``
        :param name: Build number, ``int``
        :param name: Execution node number, ``int``
        :returns: Execution node build log,  ``dict``
        '''
        folder_url, short_name = self.client._get_job_folder(name)
        try:
            response = self.client.jenkins_open(Request(
                self.client._build_url(WF_NODE_LOG, locals())
            ))
            if response:
                return json.loads(response)
            else:
                raise jenkins.JenkinsException('job[%s] number[%d] does not exist'
                                               % (name, number))
        except HTTPError:
            raise jenkins.JenkinsException('job[%s] number[%d] does not exist'
                                           % (name, number))

    def build_wf(self, name, params):
        '''Get build log for execution node. Requires Pipeline Stage View plugin.

        :param name: Job name, ``str``
        :param params: Job parameters, ``dict``
        :returns: True if API post succeeded ``bool``
        '''
        base_path = getattr(settings, 'JENKINS_API_URL')
        folder_url, short_name = self.client._get_job_folder(name)
        ext_path = '%(folder_url)sjob/%(short_name)s/buildWithParameters' % {
            'folder_url': folder_url, 'short_name': short_name}
        url = urlparse.urljoin(base_path, ext_path)
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': self.client.auth
        }
        try:
            response = requests.post(url, headers=headers, data=params)
        except Exception as e:
            msg = "Build WF request failed: %s" % repr(e)
            LOG.exception(msg)
            return False

        return True

    def _safe_response(self, response):
        esc26 = chr(26)
        return response.replace(esc26, "")

    # PATCHED VERSION OF ORIGINAL CLIENTS METHOD
    def get_job_info(self, name, depth=0, fetch_all_builds=False):
        '''Get job information dictionary.

        :param name: Job name, ``str``
        :param depth: JSON depth, ``int``
        :param fetch_all_builds: If true, all builds will be retrieved
                                 from Jenkins. Otherwise, Jenkins will
                                 only return the most recent 100
                                 builds. This comes at the expense of
                                 an additional API call which may
                                 return significant amounts of
                                 data. ``bool``
        :returns: dictionary of job information
        '''
        folder_url, short_name = self.client._get_job_folder(name)
        try:
            _response = self.client.jenkins_open(Request(
                self.client._build_url(JOB_INFO, locals())
            ))
            response = self._safe_response(_response)
            if response:
                if fetch_all_builds:
                    return self.client._add_missing_builds(json.loads(response))
                else:
                    return json.loads(response)
            else:
                raise JenkinsException('job[%s] does not exist' % name)
        except HTTPError:
            raise JenkinsException('job[%s] does not exist' % name)
        except ValueError:
            raise JenkinsException(
                "Could not parse JSON info for job[%s]" % name)

extension = JenkinsClientExtension()
extension.client = JENKINS_CLIENT

for method in [method for method in dir(extension)
               if callable(getattr(extension, method)) and not method.startswith("__")]:

    setattr(JENKINS_CLIENT, method, getattr(extension, method))

jenkins_client = JENKINS_CLIENT
