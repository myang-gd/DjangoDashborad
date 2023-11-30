from django.conf.urls import url
from .import views_api

urlpatterns = [
        url(r'^feature-product-codes/$', views_api.FeatureConfig.as_view()),
        url(r'^update-feature-product-codes/$', views_api.UpdateConfFeatureConfig.as_view())
    ]