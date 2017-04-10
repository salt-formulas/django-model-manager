from keystoneclient.exceptions import *
from openstack_auth.exceptions import KeystoneAuthException


class DevopsPortalAuthException(KeystoneAuthException):

    """Generic error class to identify and catch our own errors."""
    pass

