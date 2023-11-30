from django.conf.urls import url
from .import views_api

urlpatterns = [
        url(r'^current-sprint-detail/$', views_api.CurrentSprintDetail.as_view()),
        url(r'^valid-sprint-list/$', views_api.ValidSprintListInfo.as_view()),
        url(r'^specific-sprint-detail/$', views_api.SpecificSprintInfo.as_view()),
    ]