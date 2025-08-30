"""
URL configuration for ristorante project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login-or-register/', login_or_register, name = 'login_or_register'),
    path("register/", UserCreateView.as_view(), name = "register"),
    path("register_manager/", ManagerCreateView.as_view(), name = "register-manager"),
    path("login/", auth_views.LoginView.as_view(), name = "login"),
    path("logout/", auth_views.LogoutView.as_view(), name = "logout"),
    re_path(r'^$|^\/$|^home\/$', home, name = "home"),
    path('menu/', include('menu.urls')),
    path('tables/', include('tables.urls')),
    path('notifications/', include('notifications.urls', namespace = 'notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)