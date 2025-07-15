from django.urls import path
from products.views.generate_qr import generate_qr
from crm_deals.views.reload import reload_start

urlpatterns = [
    path('', reload_start, name='reload_start'),
    path('generate_qr', generate_qr),
]
