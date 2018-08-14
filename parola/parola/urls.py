"""parola URL Configuration

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
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('', include('main.urls')),
    path('data_sets/', include('data_sets.urls')),
    path('data_tools/', include('data_tools.urls')),
    path('parola_refine/', include('parola_refine.urls')),
    path('visualization/', include('visualization.urls')),
    path('download_manager/', include('download_manager.urls')),
    path('admin/', admin.site.urls),
]
