from django.urls import path
from django.conf.urls import url

from engage.views import EngageView, search

app_name = 'engage'
urlpatterns = [
               path('', search, name='search'),
               url('^(?P<pk>\d+)/$', EngageView.as_view(), name='build'),
               ]
