
import datetime
import logging
from django.contrib.auth import models


LOG = logging.getLogger(__name__)


def set_session_from_user(request, user):
    request.session['token'] = user.token
    request.session['user'] = user
    request.session['user_id'] = user.id
    request.session['region_endpoint'] = user.endpoint
    request.session['services_region'] = user.services_region
    # Update the user object cached in the request
    request._cached_user = user
    request.user = user


class Token(object):

    """Token object that encapsulates the auth_ref (AccessInfo)from keystone
       client.

       Added for maintaining backward compatibility with horizon that expects
       Token object in the user object.
    """

    def __init__(self, auth_ref=None):
        # User-related attributes
        if auth_ref:
            self.id = auth_ref["token"]["key"]
            self.created = auth_ref["token"]["created"]
        else:
            self.id = None
        self.expires = datetime.datetime.today() + datetime.timedelta(days=30)


def create_user_from_token(request=None, auth_ref=None):
    # if the region is provided, use that, otherwise use the preferred region

    if request:

        return User()

    token = Token(auth_ref)

    user = auth_ref["user"]

    return User(
        id=user["id"],
        username=user["username"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        operator=user["operator"],
        manager=user["manager"],
        organisation=user["organisation"],
        support_level=user["support_level"],
        key_account=user["key_account"],
        phone=user["phone"],
        token=token,
        user=user
    )


class User(models.AnonymousUser):

    """A User class with some extra special sauce for Keystone.

    In addition to the standard Django user attributes, this class also has
    the following:

    .. attribute:: token

        The Keystone token object associated with the current user/tenant.

    .. attribute:: customer

    """

    def __init__(self, id=None, token=None, user=None, roles=None,
                 authorized_tenants=None, endpoint=None, is_active=True, manager=None,
                 is_admin=False, username=None, first_name=None, last_name=None, email=None,
                 organisation=None, operator=None, support_level=None, phone=None, key_account=None):

        self.id = id
        self.pk = id

        self.token = token or Token()
        self.username = username
        self.user = user
        self.manager = manager
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.organisation = organisation
        self.operator = operator
        self.support_level = support_level
        self.roles = roles or []
        self.key_account = key_account

        self.enabled = is_active

        # openstack compatibility
        self.tenant_id = None
        self.endpoint = None
        self.services_region = None
        self.authorized_tenants = []
        self.user_domain_id = None
        self.domain_id = None
        self.project_id = None
        self.project_name = None  # self.organisation
        self.user_domain_name = None
        self.service_catalog = []

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.username)

    def name(self):
        if self.last_name and self.first_name:
            return "{} {}".format(
                self.first_name,
                self.last_name)
        return self.username

    def is_token_expired(self, margin=None):
        """Determine if the token is expired.

        Returns ``True`` if the token is expired, ``False`` if not, and
        ``None`` if there is no token set.

        .. param:: margin

           A security time margin in seconds before real expiration.
           Will return ``True`` if the token expires in less than ``margin``
           seconds of time.
           A default margin can be set by the TOKEN_TIMEOUT_MARGIN in the
           django settings.

        if self.token is None:
            return None
        return not utils.is_token_valid(self.token, margin)
        """
        return True

    def is_authenticated(self, margin=None):
        """Checks for a valid authentication.

        .. param:: margin

           A security time margin in seconds before end of authentication.
           Will return ``False`` if authentication ends in less than ``margin``
           seconds of time.
           A default margin can be set by the TOKEN_TIMEOUT_MARGIN in the
           django settings.

        """
        if hasattr(self.token, "id"):
            return True
        else:
            return False

    def is_anonymous(self, margin=None):
        """Return if the user is not authenticated.

        Returns ``True`` if not authenticated,``False`` otherwise.

        .. param:: margin

           A security time margin in seconds before end of an eventual
           authentication.
           Will return ``True`` even if authenticated but that authentication
           ends in less than ``margin`` seconds of time.
           A default margin can be set by the TOKEN_TIMEOUT_MARGIN in the
           django settings.

        """
        return not self.is_authenticated(margin)

    @property
    def is_active(self):
        return self.enabled

    @property
    def manage_organisations(self):
        """restrict operator flag for key_accounts
        """
        if self.is_operator:
            return self.key_account
        return []

    @property
    def is_operator(self):
        """Evaluates whether this user has operator privileges.

        Returns ``True`` or ``False``.
        """

        return self.operator

    @property
    def level(self):
        """returns support level as integer type
        """
        if self.is_operator:
            return int(self.support_level.replace('l', ''))
        return None

    @property
    def is_manager(self):
        return self.manager

    @property
    def is_l3(self):
        return True if self.level >= 3 else False

    @property
    def available_services_regions(self):
        """Returns list of unique region name values in service catalog."""
        regions = []
        if self.service_catalog:
            for service in self.service_catalog:
                if service['type'] == 'identity':
                    continue
                for endpoint in service['endpoints']:
                    if endpoint['region'] not in regions:
                        regions.append(endpoint['region'])
        return regions

    def save(*args, **kwargs):
        # Presume we can't write to Keystone.
        pass

    def delete(*args, **kwargs):
        # Presume we can't write to Keystone.
        pass

    # Check for OR'd permission rules, check that user has one of the
    # required permission.
    def has_a_matching_perm(self, perm_list, obj=None):
        """Returns True if the user has one of the specified permissions.

        If object is passed, it checks if the user has any of the required
        perms for this object.
        """
        # If there are no permissions to check, just return true
        if not perm_list:
            return True
        # Check that user has at least one of the required permissions.
        for perm in perm_list:
            if self.has_perm(perm, obj):
                return True
        return False

    # Override the default has_perms method. Allowing for more
    # complex combinations of permissions.  Will check for logical AND of
    # all top level permissions.  Will use logical OR for all first level
    # tuples (check that use has one permissions in the tuple)
    #
    # Examples:
    #   Checks for all required permissions
    #   ('openstack.roles.admin', 'openstack.roles.L3-support')
    #
    #   Checks for admin AND (L2 or L3)
    #   ('openstack.roles.admin', ('openstack.roles.L3-support',
    #                              'openstack.roles.L2-support'),)
    def has_perms(self, perm_list, obj=None):
        """Returns True if the user has all of the specified permissions.

        Tuples in the list will possess the required permissions if
        the user has a permissions matching one of the elements of
        that tuple
        """
        # If there are no permissions to check, just return true
        if not perm_list:
            return True
        for perm in perm_list:
            if isinstance(perm, basestring):
                # check that the permission matches
                if not self.has_perm(perm, obj):
                    return False
            else:
                # check that a permission in the tuple matches
                if not self.has_a_matching_perm(perm, obj):
                    return False
        return True
