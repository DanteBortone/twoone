from django.urls import path

from .views import HomeView, NewView

app_name = 'user'
urlpatterns = [
               path('', HomeView.as_view(), name='homepage'),
               path('new/', NewView.as_view(), name='new'),
               ]
