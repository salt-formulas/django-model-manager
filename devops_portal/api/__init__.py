from .base import BaseClient
from .users import User, Operator

class Api(BaseClient):

    users = User()
    pass

devops_portal = Api()
