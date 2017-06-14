import yaml

from django import template

register = template.Library()


@register.filter
def format_return(ret):
    try:
        content = yaml.dump(yaml.safe_load(ret), default_flow_style=False)
        out = '<pre class="return">%s</pre>' % content
    except:
        out = '<pre class="return">%s></pre>' % ret
    return out

