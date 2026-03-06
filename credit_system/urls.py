"""
URL configuration for credit_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from loans.views import api_root

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('home/', TemplateView.as_view(template_name='index.html'), name='home'),
    path('api-root/', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('loans.urls')),
]

