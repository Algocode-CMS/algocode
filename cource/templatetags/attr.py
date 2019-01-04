from django import template

register = template.Library()


@register.filter
def attr(obj, attr):
    if isinstance(obj, (list,)):
        return obj[int(attr)]
    if isinstance(obj, (dict,)):
        return obj[attr]
    return getattr(obj, attr)
