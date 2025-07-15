import random
import datetime
import pytz
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.bitrix_token import BitrixToken
from products.utils.webhook import web_hook_auth, domain
import time

USER_IDS = [1, 8, 10, 12, 14, 16]
PHONE_NUMBERS = ["+79001234567", "+79007654321", "+79001112233", "+79009998877", "+79009998866"]  # просто фиктивные номера


@main_auth(on_cookies=True)
def generate_calls(request):
    webhook_token = BitrixToken(
        web_hook_auth=web_hook_auth,
        domain=domain,
    )
    if request.method == "POST":
        timezone = pytz.timezone("Europe/Moscow")
        now = datetime.datetime.now(timezone)

        for _ in range(20):
            user_id = random.choice(USER_IDS)
            phone = random.choice(PHONE_NUMBERS)
            duration = random.randint(61, 600)  # от 1 до 10 минут

            call_start = now - datetime.timedelta(
                seconds=random.randint(0, 86400)
            )
            call_start_iso = call_start.isoformat()

            # регистрирую звонок
            data = webhook_token.call_api_method("telephony.externalcall.register", {
                "USER_ID": user_id,
                "PHONE_NUMBER": phone,
                "CALL_START_DATE": call_start_iso,
                "TYPE": 1,
                "CRM_CREATE": 0,
                "SHOW": 0,
            })

            time.sleep(0.5)
            call_id = data.get("result", {}).get("CALL_ID")
            if not call_id:
                continue  # пропускаю, если не получилось зарегистрировать

            # завершаю звонок
            data = webhook_token.call_api_method("telephony.externalcall.finish", {
                "CALL_ID": call_id,
                "USER_ID": user_id,
                "DURATION": duration,
                "STATUS_CODE": "200",
                "ADD_TO_CHAT": 0,
            })

            time.sleep(0.5)
        return redirect("list_people")
