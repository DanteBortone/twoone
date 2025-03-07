"""Twoone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('engage/', include('engage.urls')),
    path('create/', include('create.urls')),
    path('user/', include('user.urls', namespace='user')),
    path('admin/', admin.site.urls),
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
    path('accounts/', include('django.contrib.auth.urls')),
    path('forum/', include('pybb.urls', namespace='pybb')),
]
