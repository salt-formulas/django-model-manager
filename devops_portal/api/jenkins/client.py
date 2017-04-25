from __future__ import absolute_import

import xml.etree.ElementTree as ET

import jenkins
import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import Request

# Requires Pipeline Stage View plugin
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


class JenkinsClientExtension(object):

    """Base wrapper around jenkins api
    """

    def get_workflows(self):
        jobs = self.client.get_jobs()

        return jobs
        #filter(lambda job: "workflow" in job["name"], jobs)

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


extension = JenkinsClientExtension()
extension.client = JENKINS_CLIENT

for method in [method for method in dir(extension)
               if callable(getattr(extension, method)) and not method.startswith("__")]:

    setattr(JENKINS_CLIENT, method, getattr(extension, method))

jenkins_client = JENKINS_CLIENT

