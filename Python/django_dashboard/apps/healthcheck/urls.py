from django.conf.urls import url
from apps.healthcheck import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^$', login_required(views.healthcheck), name='healthcheck'),
        url(r'^server/(?P<vip_display_name>[\w\-]+)/$', login_required(views.get_all_servers), name='get_all_servers'),
        url(r'^result/$', login_required(views.result) , name='result'),
        url(r'^viewRequest/$', login_required(views.requestPopUp) , name='view_healtcheck_request'),
        url(r'^viewResponse/$', login_required(views.responsePopUp) , name='view_healtcheck_response'),
        url(r'^schedule/$', login_required(views.schedule), name='schedule'),
        url(r'^schedule_config/$', login_required(views.schedule_config) , name='schedule_config'),
        url(r'^schedule_run/$', login_required(views.schedule_run) , name='schedule_run'),
        url(r'^schedule_run_result/$', login_required(views.schedule_run_result) , name='schedule_run_result'),
        url(r'^schedule_views/$', login_required(views.schedule_views) , name='schedule_views'),
        url(r'^action_change/$', login_required(views.action_change) , name='action_change'),
        url(r'^operation_save_check/$', login_required(views.operation_save_check) , name='operation_save_check')          
    ]