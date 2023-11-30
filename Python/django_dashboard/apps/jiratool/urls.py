from django.conf.urls import url
from apps.jiratool import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^$', login_required(views.JiraTool), name='jiratool'),
        url(r'^loadSprintsByProject/$', views.loadSprints, name='loadSprintsByProject'),
        url(r'^searchJira/$', views.SearchJira, name='searchJira'),
        url(r'^assignDetail/$', views.assignDetail, name='assignDetail'),

    ]