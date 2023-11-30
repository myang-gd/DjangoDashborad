from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [        
    url(r'^customer-finder/$', login_required(views.customerFinder), name='customerFinder'),    
    url(r'^customer-config/$', login_required(views.customerFinderConfig), name='customerConfig'),
    url(r'^get-environment/$', views.getEnvironment , name='getEnvironment'),
    url(r'^get-projects/$', views.getProjects , name='getProjects'),
    url(r'^get-productmap/$', views.getProductMap , name='getProductMap'),
    url(r'^get-emailprefix/$', views.getEmailPrefix , name='getEmailPrefix'),
    url(r'^get-useridprefix/$', views.getUserIDPrefix , name='getUserIDPrefix'),
    url(r'^get-passwordrule/$', views.getPasswordRule , name='getPasswordRule'),
    url(r'^get-custtypelist/$', views.getCusttypeMapList , name='getCusttypeMapList'),
    url(r'^get-generatedsql/$', views.getQuery , name='getQuery'),
    url(r'^get-customer/$', views.getCustomer , name='getCustomer'),
    url(r'^add-customertype/$', login_required(views.addCustType), name='addCustType'),
    url(r'^add-query/$', login_required(views.addQuery), name='addQuery'),
    url(r'^add-productmap/$', login_required(views.addProductMapByProject) , name='addProductMapByProject'),
    url(r'^add-useridprefix/$', login_required(views.addUserIDPrefixByProject) , name='addUserIDPrefixByProject'),
    url(r'^add-emailprefix/$', login_required(views.addEmailPrefixByProject) , name='addEmailPrefixByProject'),
     url(r'^add-passwordrule/$', login_required(views.addPasswordRule) , name='addPasswordRule'),
    url(r'^update-customertype/$', login_required(views.updateCustType), name='updateCustType'),
    url(r'^update-query/$', login_required(views.updateQuery), name='updateQuery'),
    url(r'^update-productmap/$', login_required(views.updateProductMapByProject), name='updateProductMapByProject'), 
    url(r'^update-useridprefix/$', login_required(views.updateUserIDPrefixByProject), name='updateUserIDPrefixByProject'),
    url(r'^update-emailprefix/$', login_required(views.updateEmailPrefixByProject), name='updateEmailPrefixByProject'),
    url(r'^update-passwordrule/$', login_required(views.updatePasswordRule), name='updatePasswordRule'),
    url(r'^enabledisable-custtype/$', login_required(views.enableDisableCustType), name='enableDisableCustType'),
    url(r'^enabledisable-productmap/$', login_required(views.enableDisableProductMap), name='enableDisableProductMap'),
    url(r'^enabledisable-useridprefix/$', login_required(views.enableDisableUserIDPrefix), name='enableDisableUserIDPrefix'),
    url(r'^enabledisable-emailprefix/$', login_required(views.enableDisableEmailPrefix), name='enableDisableEmailPrefix'),
    url(r'^enabledisable-passwordrule/$', login_required(views.enableDisablePasswordRule), name='enableDisablePasswordRule'),
    url(r'^enabledisable-subquery/$', login_required(views.enableDisableSubQuery), name='enableDisableSubQuery'),
    url(r'^load-queries/$', views.loadQuerysByCustType, name='loadQuerysByCustType')  
]
