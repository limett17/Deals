from integration_utils.bitrix24.bitrix_token import BitrixToken
from products.utils.webhook import web_hook_auth, domain


def get_product_from_bitrix(product_id):
    webhook_token = BitrixToken(
        web_hook_auth=web_hook_auth,
        domain=domain,
    )

    data = webhook_token.call_api_method('crm.product.get', params={"ID": product_id})
    product = data.get("result", {})

    data = webhook_token.call_api_method('catalog.productImage.list', params={
        "productId": product_id,
        "select": ["id", "name", "productId", "type", "createTime", "downloadUrl", "detailUrl"]
    })
    image = data.get("result", {}).get('productImages', {})
    image = image[0]['detailUrl']

    if not product:
        return None

    return {
        'product': product,
        'image': image
    }
