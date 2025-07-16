from django.urls import path
from .views.company_map import company_map

urlpatterns = [
    path('map/', company_map, name='company_map'),
]
