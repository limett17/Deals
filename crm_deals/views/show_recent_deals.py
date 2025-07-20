from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from datetime import datetime


def format_date(iso_date):
    if iso_date:
        try:
            return datetime.fromisoformat(iso_date).strftime('%d-%m-%Y')
        except ValueError:
            return iso_date[:10]
    return None


@main_auth(on_cookies=True)
def show_recent_deals(request):
    but = request.bitrix_user_token
    res = but.call_api_method("crm.deal.list", {
        "order": {"DATE_CREATE": "DESC"},
        "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "DATE_CREATE", "UF_CRM_1752059330",
                   "UF_CRM_1752056545", "UF_CRM_1752057390", "UF_CRM_1752056648"],
        "start": 0,
        "limit": 10
    })['result']

    recent_deals = res[:10]
    for deal in recent_deals:
        deal['DATE_CREATE'] = format_date(deal['DATE_CREATE'])
        if "UF_CRM_1752056545" in deal:
            deal["UF_CRM_1752056545"] = format_date(deal["UF_CRM_1752056545"])

    return render(request, 'showrecentdeals.html', {"recent_deals": recent_deals})

