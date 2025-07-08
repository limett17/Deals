from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


@main_auth(on_cookies=True)
def show_recent_deals(request):
    but = request.bitrix_user_token
    res = but.call_api_method("crm.deal.list", {
        "order": {"DATE_CREATE": "DESC"},
        "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "DATE_CREATE"],
        "start": 0,
        "limit": 10
    })['result']

    recent_deals = res[:10]
    return render(request, 'showrecentdeals.html', locals())
