from django import template
from apps.healthcheck.models import Vip

register = template.Library()

@register.inclusion_tag('all_vips.html')
def get_vip_list(vip=None):
    return {'vips': Vip.objects.all(), 'active_vip': vip}

@register.filter
def get_type(value):
    return type(value)