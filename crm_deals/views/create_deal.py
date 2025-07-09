from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


@main_auth(on_cookies=True)
def create_deal(request):
    if request.method == "POST":
        title = request.POST.get("title")
        opportunity = request.POST.get("opportunity")
        delivery_method = request.POST.get("delivery_method")
        delivery_date = request.POST.get("delivery_date")
        delivery_time = request.POST.get("delivery_time")
        delivery_instructions = request.POST.get("delivery_instructions")

        user_token = request.bitrix_user_token
        res = user_token.call_api_method("crm.deal.add", {
            "fields": {
                "TITLE": title,
                "OPPORTUNITY": opportunity,
                "UF_CRM_1752059330": delivery_method,
                "UF_CRM_1752056545": delivery_date,
                "UF_CRM_1752057390": delivery_time,
                "UF_CRM_1752056648": delivery_instructions
            }
        })

        if 'error' in res:
            return render(request, 'createdeal.html', {"error": res})
        return render(request, 'deal_success.html', {'deal_result': res})
    else:
        return render(request, 'createdeal.html')
