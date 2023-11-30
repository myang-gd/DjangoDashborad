from django import template
import uuid
register = template.Library()

@register.simple_tag
def get_uuid():
    return str(uuid.uuid4())