#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devops_portal.base_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
