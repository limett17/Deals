import requests
from products.utils.webhook import WEBHOOK_URL, IMAGES_WEBHOOK


def get_product_from_bitrix(product_id):
    response = requests.get(WEBHOOK_URL, params={"ID": product_id})
    data = response.json()
    product = data.get("result", {})
    #print(product)
    payload = {
        "productId": product_id,
        "select": ["id", "name", "productId", "type", "createTime", "downloadUrl", "detailUrl"]
    }

    response = requests.post(IMAGES_WEBHOOK, json=payload)
    data = response.json()
    image = data.get("result", {}).get('productImages', {})
    #print(image)
    image = image[0]['detailUrl']
    #print(image)
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