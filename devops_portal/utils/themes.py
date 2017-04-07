import threading

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.utils._os import safe_join  # noqa
from horizon.themes import ThemeTemplateLoader as HorizonThemeTemplateLoader


# Local thread storage to retrieve the currently set theme
_local = threading.local()


# Get the themes from settings
def get_themes():
    return getattr(settings, 'AVAILABLE_THEMES', [])


# Get the default theme
def get_default_theme():
    return getattr(settings, 'DEFAULT_THEME', 'default')


# Find the theme tuple
def find_theme(theme_name):
    for each_theme in get_themes():
        if theme_name == each_theme[0]:
            return each_theme

    return None


class ThemeTemplateLoader(HorizonThemeTemplateLoader):

    def get_template_sources(self, template_name):

        # If the cookie doesn't exist, set it to the default theme
        default_theme = get_default_theme()
        theme = getattr(_local, 'theme', default_theme)
        this_theme = find_theme(theme)

        # If the theme is not valid, check the default theme ...
        if not this_theme:
            this_theme = find_theme(get_default_theme())

            # If the theme is still not valid, then move along ...
            # these aren't the templates you are looking for
            if not this_theme:
                pass

        try:
            if not template_name.startswith('/'):
                try:
                    yield safe_join(
                        'devops_portal',
                        this_theme[2],
                        'templates',
                        template_name
                    )
                except SuspiciousFileOperation:
                    yield os.path.join(
                        this_theme[2], 'templates', template_name
                    )

        except UnicodeDecodeError:
            # The template dir name wasn't valid UTF-8.
            raise
        except ValueError:
            # The joined path was located outside of template_dir.
            pass

