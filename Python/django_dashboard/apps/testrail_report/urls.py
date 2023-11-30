from django.conf.urls import url
from . import views
from .views import CoverageView
from django.contrib.auth.decorators import login_required

urlpatterns = [  # /testrail_report/
    url(r'^$', login_required(views.ReportView.as_view()), name='testrail_report'),
    url(r'coverage/', login_required(CoverageView.as_view()), name='coverage'),
    url(r'^download$', login_required(views.download), name='download'),
    url(r'coverage_api/', views.confluence_using_coverage, name='coverage_api'),
]
