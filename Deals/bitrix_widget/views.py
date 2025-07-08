from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from django.conf import settings

@main_auth(on_start=True, set_cookie=True)
def index(request):
    app_settings = settings.APP_SETTINGS
    print(request.GET)
    return render(request, 'bitrix_widget/index.html', locals())




