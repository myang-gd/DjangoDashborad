from django import template
from ..import views,models 
from django.core.urlresolvers import reverse
import json
register = template.Library()

@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__

@register.inclusion_tag('all_support_sidelinks.html')
def get_support_side(user=None):
    returnList = []
    teams = []
    for team in models.Team.objects.all():
        team_map = {}
        team_map['text'] = team.name
        team_map['href'] = reverse(views.CONFIGMODIFIER_TEAM,args=[team.id])
        teams.append(team_map)
    if user:
        returnList.append({"name":"Home", "link": reverse(views.CONFIGMODIFIER)})
        if user.has_perm('ConfigModifier.add_entry'):
            returnList.append({"name":"Create Entry", "link": reverse(views.CONFIGMODIFIER_ENTRYSELECT)})
        
        returnList.append({"name":"Make Request", "link": reverse(views.CONFIGMODIFIER_MAKEREQUEST)})
        if views.can_change_supend(user):
            returnList.append({"name":"RE", "link": reverse(views.CONFIGMODIFIER_CM)})
           
    return {'sides': returnList,'teams':json.dumps(teams)}

@register.filter(name='isspace')
def isspace(value):
    return value != None and value.replace('"','').isspace()

