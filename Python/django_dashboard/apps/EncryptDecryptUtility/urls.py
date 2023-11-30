from django.conf.urls import url
from apps.EncryptDecryptUtility import views
from django.contrib.auth.decorators import login_required
 
urlpatterns = [
    url(r'^$', login_required(views.EncryptDecryptUtility), name='encryptDecryptUtility'),   
    url(r'^encrypt_decrypt/$', login_required(views.encryptDecrypt), name='encrypt_decrypt'),
    url(r'^get_project_list/$', login_required(views.getProjects), name='get_project_list'),
    url(r'^tokenization/$', login_required(views.TokenizationUtility), name='TokenizationUtility'),
    url(r'^tokenization/tokenize$', login_required(views.Tokenize), name='tokenize'),
    url(r'^tokenization/detokenize$', login_required(views.DeTokenize), name='detokenize')

]

