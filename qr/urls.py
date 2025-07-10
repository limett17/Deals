from django.urls import path
from qr.views.show_product_by_code import show_product_by_code


urlpatterns = [
    path('<str:secret_code>', show_product_by_code),
]
