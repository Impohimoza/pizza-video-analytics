from django import template

register = template.Library()


@register.simple_tag
def query_transform(request_get):
    if not request_get:
        return ''
    return '&'.join([f"{key}={value}" for key, value in request_get.items()])