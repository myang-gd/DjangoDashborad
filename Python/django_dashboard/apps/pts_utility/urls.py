from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
 
urlpatterns = [
    url(r'^$', login_required(views.pts_utility), name='pts_utility'),
    url(r'^get_cvv$', login_required(views.get_cvv), name='get_cvv'),
    url(r'^get_pts_card_info$', login_required(views.get_pts_card_info), name='get_pts_card_info')
]

