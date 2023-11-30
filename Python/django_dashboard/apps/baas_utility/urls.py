from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
 
urlpatterns = [
    url(r'^$', login_required(views.baas_utility), name='baas_utility'),
    url(r'^get_card_info$', login_required(views.get_card_info), name='get_card_info')
]

