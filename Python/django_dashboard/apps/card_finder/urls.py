from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', login_required(views.card_finder), name='card_finder'),
    url(r'^get-productmap/$', login_required(views.getProductMap) , name='getProductMap'),    
#     url(r'^inventory', views.card_inventory, name='card_inventory'),
]