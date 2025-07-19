from django.contrib import admin
from django.urls import path, include
from start.views.start import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('deals/', include('crm_deals.urls')),
    path('products/', include('products.urls')),
    path('p/', include('qr.urls')),
    path('people/', include('people.urls')),
    path('company/', include('map.urls')),
    path('contacts/', include('contacts.urls')),
]
