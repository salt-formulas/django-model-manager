import horizon
from django.utils.translation import ugettext_lazy as _


class Cookiecutter(horizon.Panel):
    name = _("Model Designer")
    slug = 'model-designer'