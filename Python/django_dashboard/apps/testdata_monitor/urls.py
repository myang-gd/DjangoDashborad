from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^testdatamonitor_config/$', login_required(views.testdata_monitor_config), name='testdataMonitorConfig'),
    url(r'^get_customertypelist$', login_required(views.loadCustTypes), name='loadCustTypes'),
    url(r'^get_monitorlist$', login_required(views.loadMonitors), name='loadMonitors'),
    url(r'^get_actionlist$', login_required(views.getActions), name='getActions'),
    url(r'^load_customertypes$', login_required(views.loadCustTypes), name='loadCustTypes'),
    url(r'^load_monitors$', login_required(views.loadMonitors), name='loadMonitors'),
    url(r'^add_customertype$', login_required(views.addCustType), name='addCustType'),
    url(r'^update_customertype$', login_required(views.updateCustType), name='updateCustType'),
    url(r'^delete_customertype$', login_required(views.deleteCustType), name='deleteCustType'),
    url(r'^add_monitor$', login_required(views.addMonitor), name='addMonitor'),
    url(r'^update_monitor$', login_required(views.updateMonitor), name='updateMonitor'),
    url(r'^delete_monitor$', login_required(views.deleteMonitor), name='deleteMonitor'),
    url(r'^load_mappings$', login_required(views.loadMappings), name='loadMappings'),
    url(r'^load_chains$', login_required(views.loadChains), name='loadChains'),
    url(r'^add_chain$', login_required(views.addChain), name='addChain'),
    url(r'^update_chain$', login_required(views.updateChain), name='updateChain'),
    url(r'^delete_chain$', login_required(views.deleteChain), name='deleteChain'),
    url(r'^add_mapping$', login_required(views.addMapping), name='addMapping'),
    url(r'^update_mapping$', login_required(views.updateMapping), name='updateMapping'),
    url(r'^delete_mapping$', login_required(views.deleteMapping), name='deleteMapping'),
    url(r'^get_projectlist$', login_required(views.getProjects), name='getProjects'),
    url(r'^testdatamonitor/$', login_required(views.testdata_monitor), name='testdataMonitor'),
    url(r'^testdatamonitor_runs/([0-9]+)$', login_required(views.testdata_monitor_runs), name='testdataMonitorRuns'),
    url(r'^schedule_monitor$', login_required(views.scheduleMonitor), name='scheduleMonitor'),
    url(r'^run_monitor$', login_required(views.runMonitor), name='runMonitor'),
    url(r'^testdatamonitor_rundetails/([0-9]+)$', login_required(views.testdata_monitor_run_details), name='testdataMonitorRunDetails'), 
    
    
    
]