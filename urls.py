from django.contrib import admin
from django.urls import path, include
from start.views.start import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('deals/', include('crm_deals.urls')),
]
