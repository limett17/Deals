from django.http import Http404
from django.shortcuts import render, get_object_or_404
from products.models import QRCodeLink
from products.utils.get_product_from_bitrix import get_product_from_bitrix


def show_product_by_code(request, secret_code):
    link = get_object_or_404(QRCodeLink, secret_code=secret_code)
    product = get_product_from_bitrix(link.product_id)
    image = product['image']
    product = product['product']
    id = product["ID"]
    name = product["NAME"]
    price = product["PRICE"]
    currency = product["CURRENCY_ID"]
    description = product["DESCRIPTION"]
    return render(request, "product_page.html", {
        "id": id,
        "name": name,
        "img": image,
        "price": price,
        "description": description,
        'currency': currency,
    })