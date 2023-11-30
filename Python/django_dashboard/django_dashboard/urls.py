"""django_dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  url(r'^admin/', include(admin.site.urls)),
                  url(r'^healthcheck/', include('apps.healthcheck.urls')),
                  url(r'^monitor/', include('apps.qa_monitor.urls')),
                  url(r'^spfinder/', include('apps.spfinder.urls')),
                  url(r'^testrail_report/', include('apps.testrail_report.urls')),
                  url(r'^case_report/', include('apps.case_report.urls')),
                  url(r'^cardfinder/', include('apps.card_finder.urls')),
                  url(r'^customerfinder/', include('apps.customerFinder.urls')),
                  url(r'^ptsutility/', include('apps.pts_utility.urls')),
                  url(r'^aciutility/', include('apps.aci_utility.urls')),
                  url(r'^baasutility/', include('apps.baas_utility.urls')),
                  url(r'^encryptdecryptutility/', include('apps.EncryptDecryptUtility.urls')),
                  url(r'^configModifier/', include('apps.ConfigModifier.urls')),
                  url(r'^login', views.login, {'template_name': 'login.html'}, name='login'),
                  url(r'^logout', views.logout, {'template_name': 'logout.html'}, name='logout'),
                  url(r'^testdatamonitor/', include('apps.testdata_monitor.urls')),
                  url(r'^JiraTool/', include('apps.jiratool.urls')),
                  url(r'^CalendarAPI/', include('apps.CommonAPI.CalendarAPI.urls')),
                  url(r'^MilestoneAPI/', include('apps.CommonAPI.MilestoneAPI.urls')),
                  url(r'^query/', include('apps.query_view.urls')),
                  url(r'^dmwncardfinder/', include('apps.dmwn_card_finder.urls')),
                  url(r'^browserstack/', include('apps.BrowserStack.urls')),
                  url(r'^dynamodb/', include('apps.CommonAPI.DynamoDB.urls')),
                  url(r'^conf/', include('apps.CommonAPI.ConfAPI.urls')),
                  url(r'^license/', include('apps.License.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
