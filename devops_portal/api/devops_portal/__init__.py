from .base import BaseClient
from .jobs import Job
from .users import User, Operator

class Api(BaseClient):

    jobs = Job()
    users = User()

devops_portal = Api()
