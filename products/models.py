from django.db import models


class QRCodeLink(models.Model):
    product_id = models.IntegerField()
    secret_code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)