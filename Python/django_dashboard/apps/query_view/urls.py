from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from apps.query_view.views import RegisterView, EditView, QuerySplitterView

urlpatterns = [
    url(r'register', login_required(RegisterView.as_view()), name='register'),
    url(r'queries', login_required(QuerySplitterView.as_view()), name='queries'),
    url(r'edit', login_required(EditView.as_view()), name='edit'),

]