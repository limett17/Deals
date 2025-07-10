from django.urls import path
from products.views.generate_qr import generate_qr


urlpatterns = [
    path('generate_qr', generate_qr),
]
