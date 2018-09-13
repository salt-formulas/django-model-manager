# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

from django.conf import settings
from django import template


register = template.Library()


@register.inclusion_tag('context_selection/_anti_clickjack.html',
                        takes_context=True)
def iframe_embed_settings(context):
    disallow_iframe_embed = getattr(settings,
                                    'DISALLOW_IFRAME_EMBED',
                                    True)
    context = {'disallow_iframe_embed': disallow_iframe_embed}
    return context
