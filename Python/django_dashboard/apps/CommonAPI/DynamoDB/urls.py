from django.conf.urls import url
from .import views_api

urlpatterns = [
        url(r'^query/$', views_api.Query.as_view())
    ]