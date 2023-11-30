from rest_framework import routers
from apps.query_api import views
from django.conf.urls import url, include

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'query_scripts', views.QueryScriptViewSet)
router.register(r'databases', views.DatabaseViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'favorites', views.FavoriteViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'my_queries/', views.my_queries),
    url(r'favorite_queries/', views.favorite_queries),
    url(r'recent_queries/', views.recent_queries),
    url(r'search_queries/', views.search_queries),
    url(r'execute_query/', views.execute_query),
    url(r'debug_query/', views.debug_query),
    url(r'save_query/', views.save_query),
    url(r'load_query/', views.load_query),
    url(r'delete_query/', views.delete_query),
    url(r'load_database_by_target/', views.load_database_by_target),
    url(r'sync_favorite/', views.sync_favorite),
    url(r'execute_query_from_case/', views.execute_query_from_case),
    url(r'sync_query_from_jvm/', views.sync_query_from_jvm),
    url(r'quick_update_query/', views.quick_update_query),
    url(r'cancel_query/', views.cancel_query),

]