from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.license, name='license'), 
    url(r'^get_user/$', views.get_user, name='get_user'),
    url(r'^check_disable_account/$', views.check_disable_account, name='check_disable_account'),
    url(r'^check_free_license/$', views.check_free_license, name='check_free_license'),   
    url(r'^encrypt/$', views.encrypt, name='encrypt')  
     
]