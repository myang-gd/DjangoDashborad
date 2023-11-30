from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # url(r'^apps/(?P<os>[\w]+)$', views.apps, name='BrowserStackApps'),
    url(r'^apps$', login_required(views.apps), name='BrowserStackApps'),
]