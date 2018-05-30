# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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

from requests import exceptions as requests


class ClientException(Exception):
    """
    The base exception class for all exceptions.
    """
    def __init__(self, code, message=None, details=None,
                 request_id=None, response=None):
        self.code = code
        self.message = message or getattr(self.__class__, 'message', None)
        self.details = details
        self.request_id = request_id

    def __str__(self):
        formatted_string = "%s" % self.message
        if self.code >= 100:
            # HTTP codes start at 100.
            formatted_string += " (HTTP %s)" % self.code
        if self.request_id:
            formatted_string += " (Request-ID: %s)" % self.request_id

        return formatted_string


class Unauthorized(ClientException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    http_status = 401
    message = "Unauthorized"


class NotFound(ClientException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    message = "Not found"


UNAUTHORIZED = (
    Unauthorized,
)


NOT_FOUND = (
    NotFound,
)


RECOVERABLE = (
    requests.RequestException,
)
