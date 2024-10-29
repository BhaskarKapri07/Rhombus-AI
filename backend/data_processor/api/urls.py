"""
URL configuration for data processing API.

Defines the routing for file processing and type update endpoints.
"""

from django.urls import path
from .views import ProcessFileView, UpdateTypesView  

urlpatterns = [
    path('process-file/', ProcessFileView.as_view(), name='process-file'),
    path('update-types/', UpdateTypesView.as_view(), name='update-types'),  
]