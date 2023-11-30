from django.conf.urls import url
from apps.spfinder import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^$', login_required(views.spfinder), name='spfinder'),
        url(r'^get_progress/$', login_required(views.getProgress), name='view_spfinder_get_progress'),
    ]