from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


@main_auth(on_cookies=True)
def create_deal(request):
    if request.method == "POST":
        title = request.POST.get("title")
        opportunity = request.POST.get("opportunity")
        custom_note = request.POST.get("custom_note")

        user_token = request.bitrix_user_token
        res = user_token.call_api_method("crm.deal.add", {
            "fields": {
                "TITLE": title,
                "OPPORTUNITY": opportunity,
                "UF_CRM_MY_STRING": custom_note
            }
        })

        if 'error' in res:
            return render(request, 'createdeal.html', {"error": res})
        return render(request, 'deal_success.html', {'deal_result': res})
    else:
        return render(request, 'createdeal.html')
