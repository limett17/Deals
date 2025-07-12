import requests
from products.utils.webhook import WEBHOOK_URL


def get_product_from_bitrix(product_id):
    response = requests.get(WEBHOOK_URL+'crm.product.get.json', params={"ID": product_id})
    data = response.json()
    product = data.get("result", {})

    payload = {
        "productId": product_id,
        "select": ["id", "name", "productId", "type", "createTime", "downloadUrl", "detailUrl"]
    }
    response = requests.post(WEBHOOK_URL+'catalog.productImage.list', json=payload)
    data = response.json()
    image = data.get("result", {}).get('productImages', {})
    image = image[0]['detailUrl']

    if not product:
        return None
    print({
        'product': product,
        'image': image
    })
    return {
        'product': product,
        'image': image
    }