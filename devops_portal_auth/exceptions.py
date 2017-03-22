
from keystoneclient.exceptions import *
from openstack_auth.exceptions import KeystoneAuthException


class DevopsAuthAuthException(KeystoneAuthException):

    """Generic error class to identify and catch our own errors."""
    pass
