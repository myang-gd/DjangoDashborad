from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from apps.aci_utility import views

urlpatterns = [
    url(r'^$', login_required(views.aci_utility), name='aci_utility'),
    url(r'^get_aci_card_info$', login_required(views.get_aci_card_info), name='get_aci_card_info'),
]

