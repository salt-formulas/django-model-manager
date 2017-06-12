from django import template

register = template.Library()

LAYOUT_CLASSES = {
    'full': 'col-sm-12',
    'half': 'col-sm-6',
    'third': 'col-sm-4',
    'quarter': 'col-sm-3'
}


@register.filter
def layout_class(width):
    return LAYOUT_CLASSES.get(width, 'full')

