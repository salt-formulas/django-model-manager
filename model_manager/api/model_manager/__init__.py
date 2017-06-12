from .base import BaseClient
from .users import User, Operator
from .organisations import Organisation


class Api(BaseClient):

    users = User()
    operators = Operator()
    organisations = Organisation()

model_manager = Api()

