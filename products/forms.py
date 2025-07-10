from django import forms


class QRCodeForm(forms.Form):
    product_id = forms.CharField(label="Product ID", max_length=100)
