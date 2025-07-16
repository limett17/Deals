import requests
from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.bitrix_token import BitrixToken
from products.utils.webhook import web_hook_auth, domain


@main_auth(on_cookies=True)
def company_map(request):
    webhook_token = BitrixToken(
        web_hook_auth=web_hook_auth,
        domain=domain,
    )
    companies = webhook_token.call_api_method('crm.company.list', params={
        'select': ["ID", "TITLE"]
    }).get('result', {})
    addresses = webhook_token.call_api_method('crm.address.list', params={
        'select': [
            'ENTITY_ID',
            'ADDRESS_1'
        ]
    }).get('result', {})

    address_dict = {item['ENTITY_ID']: item['ADDRESS_1'] for item in addresses}
    merged = []
    for company in companies:
        company_id = company['ID']
        merged.append({
            'ID': company_id,
            'TITLE': company['TITLE'],
            'ADDRESS': address_dict.get(company_id, 'Адрес не найден')
        })

    points = []
    for company in merged:
        address = company['ADDRESS']
        address_req = '+'.join(address.split(' '))
        address_req = 'Санкт-Петербург+'+address_req
        coords = requests.get(f'https://geocode-maps.yandex.ru/v1/?apikey=59fdd512-90eb-464b-9605-bc86a1bc89a7&geocode={address_req}&format=json').json()
        coords = coords['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        coords = coords.split(' ')[::-1]
        coords = [float(coord) for coord in coords]
        company_name = company['TITLE']
        points.append({
            "name": company_name,
            "coords": coords
        })
    return render(request, 'company_map.html', context={
        'points': points
    })
