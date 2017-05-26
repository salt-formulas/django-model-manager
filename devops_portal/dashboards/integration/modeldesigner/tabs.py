from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from horizon import tabs
from devops_portal.api.jenkins import jenkins_client

JOB_ID = getattr(settings, 'COOKIECUTTER_JENKINS_JOB')


class OutputTab(tabs.Tab):
    name = _("Console Output")
    slug = "console_output"
    template_name = "integration/modeldesigner/tabs/_tab_output.html"
    preload = False

    def get_context_data(self, request, **kwargs):
        """This method should return a dictionary of context data used to
        render the tab. Required.
        """
        job_id = JOB_ID
        build_id = self.tab_group.kwargs['build_id']
        output = jenkins_client.get_build_console_output(job_id, int(build_id))
        return {'output': output}


class WorkflowTab(tabs.Tab):
    name = _("Workflow")
    slug = "workflow"
    template_name = "integration/modeldesigner/tabs/_tab_workflow.html"
    preload = False

    def parse_nodes(self, node_list, job_id, build_id):
        """
        node_list is list ['actions'][index]['nodes'] from
        get_build_info api call response
        """
        # Define jenkins classes
        flow_start = 'org.jenkinsci.plugins.workflow.graph.FlowStartNode'
        step_start = 'org.jenkinsci.plugins.workflow.cps.nodes.StepStartNode'
        step_atom = 'org.jenkinsci.plugins.workflow.cps.nodes.StepAtomNode'
        step_end = 'org.jenkinsci.plugins.workflow.cps.nodes.StepEndNode'
        flow_end = 'org.jenkinsci.plugins.workflow.graph.FlowEndNode'

        # Define stage display names
        stage_start = 'Stage : Start'
        stage_end = 'Stage : End'

        nodes = []
        cur = None

        # Parse steps and their atoms from node_list
        for idx, node in enumerate(node_list):
            # STEP START
            if node['_class'] == step_start:
                if node_list[idx-1]['displayName'] == stage_start:
                    nodes.append({
                        'displayName': node['displayName'],
                        'url': node['url'],
                        'running': node['running'],
                        'iconColor': node['iconColor'],
                        'id': node['id'],
                        'atoms': []
                    })
 
                    cur = next(i for (i, d) in enumerate(nodes) if d.get('id', -1) == node['id'])
                elif cur:
                    print "GET_WF_NODE_LOG"
                    text = jenkins_client.get_wf_node_log(job_id, int(build_id), int(node['id'])).get('text', '')
                    nodes[cur]['atoms'].append({
                        'displayName': node['displayName'],
                        'url': node['url'],
                        'running': node['running'],
                        'iconColor': node['iconColor'],
                        'text': text,
                        'id': node['id']
                    })
            # STEP ATOM
            elif node['_class'] == step_atom and cur:
                text = jenkins_client.get_wf_node_log(job_id, int(build_id), int(node['id'])).get('text', '')
                nodes[cur]['atoms'].append({
                    'displayName': node['displayName'],
                    'url': node['url'],
                    'running': node['running'],
                    'iconColor': node['iconColor'],
                    'text': text,
                    'id': node['id']
                })
            # STEP END
            elif node['_class'] == step_end:
                if node_list[idx+1]['displayName'] == stage_end:
                    nodes[cur]['iconColor'] = node['iconColor']
                    cur = None
                elif cur:
                    nodes[cur]['atoms'].append({
                        'displayName': node['displayName'],
                        'url': node['url'],
                        'running': node['running'],
                        'iconColor': node['iconColor'],
                        'text': text,
                        'id': node['id']
                    })

        return nodes

    def get_context_data(self, request, **kwargs):
        """This method should return a dictionary of context data used to
        render the tab. Required.
        """
        job_id = JOB_ID
        build_id = self.tab_group.kwargs['build_id']
        build = jenkins_client.get_build_info(job_id, int(build_id), depth=3)
        index = next(i for (i, d) in enumerate(build['actions']) if d.get('nodes', None))
        nodes = {}
        if isinstance(index, int):
            node_list = build['actions'][index]['nodes']
            nodes = self.parse_nodes(node_list, job_id, build_id)

        return {'nodes': nodes}


class ParamTab(tabs.Tab):
    name = _("Parameters")
    slug = "params"
    template_name = "integration/modeldesigner/tabs/_tab_param.html"
    preload = False

    def get_context_data(self, request, **kwargs):
        """This method should return a dictionary of context data used to
        render the tab. Required.
        """
        job_id = JOB_ID
        build_id = self.tab_group.kwargs['build_id']
        build = jenkins_client.get_build_info(job_id, int(build_id), depth=1)
        parameters = {}
        index = next(i for (i, d) in enumerate(build['actions']) if 'hudson.model.ParametersAction' in d.get('_class', ''))
        if isinstance(index, int):
            parameters = build['actions'][index]['parameters']

        return {'parameters': parameters}


class DetailTabGroup(tabs.TabGroup):
    slug = "build_details"
    tabs = (ParamTab, OutputTab, WorkflowTab)
    sticky = True
    show_single_tab = True

