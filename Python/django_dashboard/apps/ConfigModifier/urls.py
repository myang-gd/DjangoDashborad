from django.conf.urls import url
from .import views, views_api
from django.contrib.auth.decorators import login_required


urlpatterns = [
        url(r'^$', login_required(views.configModifier), name=views.CONFIGMODIFIER),  
        url(r'^entrySelect/$', login_required(views.entrySelect), name=views.CONFIGMODIFIER_ENTRYSELECT),
        url(r'^entryAdd/$', login_required(views.entryAdd), name=views.CONFIGMODIFIER_ENTRYADD),    
        url(r'^entryResult/$', login_required(views.entryResult), name=views.CONFIGMODIFIER_ENTRYRESULT),
        url(r'^makeRequest/$', login_required(views.makeRequest), name=views.CONFIGMODIFIER_MAKEREQUEST),
        url(r'^team/(?P<pk>[0-9]+)/$', login_required(views.team), name=views.CONFIGMODIFIER_TEAM),
        url(r'^feature/(?P<pk>[0-9]+)/(?P<action>[\w]+)/$', login_required(views.feature), name=views.CONFIGMODIFIER_FEATURE),
        url(r'^Request/(?P<pk>[0-9]+)/(?P<action>[\w]+)/$', login_required(views.request), name=views.CONFIGMODIFIER_REQUEST),
        url(r'^cm/$', login_required(views.cm), name=views.CONFIGMODIFIER_CM),
        url(r'^ajax/$', login_required(views.ajax), name=views.CONFIGMODIFIER_AJAX),
        url(r'^locks/$', views_api.CurrentLocksList.as_view()),
        url(r'^locks/(?P<pk>[0-9]+)/$', views_api.CurrentLocksDetail.as_view()),
        url(r'^servers/$', views_api.ServersList.as_view()),
        url(r'^servers/(?P<pk>[0-9]+)/$', views_api.ServersDetail.as_view()),
        url(r'^users/$', views_api.UsersList.as_view()),
        url(r'^users/(?P<pk>[0-9]+)/$', views_api.UsersDetail.as_view()),
        url(r'^fields/$', views_api.FieldsList.as_view()),
        url(r'^fields/(?P<pk>[0-9]+)/$', views_api.FieldsDetail.as_view()),
        url(r'^environments/$', views_api.EnvironmentsList.as_view()),
        url(r'^environments/(?P<pk>[0-9]+)/$', views_api.EnvironmentsDetail.as_view()),
        url(r'^environments/color_stack/(?P<env_name>\w+)/$', views_api.EnvironmentsColorStack.as_view()),
        url(r'^filemaps/$', views_api.FilemapsList.as_view()),
        url(r'^filemaps/(?P<pk>[0-9]+)/$', views_api.FilemapsDetail.as_view()),
        url(r'^servertypes/$', views_api.ServerTypesList.as_view()),
        url(r'^servertypes/(?P<pk>[0-9]+)/$', views_api.ServerTypesDetail.as_view()),
        url(r'^suspendActivities/$', views_api.SuspendActivityList.as_view()),
        url(r'^suspendActivities/(?P<pk>[0-9]+)/$', views_api.SuspendActivityDetail.as_view()),
    ]