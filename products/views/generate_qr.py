from django.shortcuts import render, redirect
import uuid
import qrcode
import io
import base64

from products.forms import QRCodeForm
from products.models import QRCodeLink
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from products.utils.get_product_from_bitrix import get_product_from_bitrix


@main_auth(on_cookies=True)
def generate_qr(request):
    qr_image_base64 = None
    generated_url = None

    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            product, _ = get_product_from_bitrix(product_id)

            if not product:
                form.add_error('product_id', 'Товар не найден в Bitrix24.')
            else:
                secret_code = uuid.uuid4().hex
                QRCodeLink.objects.create(product_id = product_id, secret_code = secret_code)

                generated_url = request.build_absolute_uri(f"/p/{secret_code}")

                img = qrcode.make(generated_url)
                buffer = io.BytesIO()
                img.save(buffer, 'PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                qr_image_base64 = f"data:image/png;base64,{img_str}"

    else:
        form = QRCodeForm()
    return render(request, 'generate_qr.html', {
        'form': form,
        'qr_image_base64': qr_image_base64,
        'generated_url': generated_url

    })
