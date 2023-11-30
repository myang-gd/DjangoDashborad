from django import template
import uuid
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
@register.simple_tag
def get_uuid():
    return str(uuid.uuid4())