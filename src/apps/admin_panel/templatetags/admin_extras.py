from django import template

register = template.Library()


@register.filter
def getattr(obj, attr):
    return __builtins__["getattr"](obj, attr, False)
