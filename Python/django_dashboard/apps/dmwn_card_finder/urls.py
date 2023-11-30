from django.conf.urls import url
from . import views
 
urlpatterns = [
    url(r'^$', views.dmwn_card_finder, name='dmwn_card_finder'),
    url(r'^get_card_details$', views.get_card_details, name='get_card_details'),
]

