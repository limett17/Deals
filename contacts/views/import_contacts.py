from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from contacts.services.importer import import_contacts_from_file
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from django.contrib import messages


@csrf_exempt
@main_auth(on_cookies=True)
def import_contacts(request):
    but = request.bitrix_user_token

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            result = import_contacts_from_file(but, uploaded_file)

            success_count = len(result.successes)
            error_count = len(result.errors)

            if result.all_ok:
                messages.success(request, f"Успешно импортировано {success_count} контактов.")
            else:
                messages.warning(request,
                                 f"Импорт завершен с частичными ошибками: {success_count} успешных, {error_count} неудач.")
                request.session["import_errors"] = result.errors

            return redirect('contacts')  # или 'contacts_import_summary'

    return render(request, 'import_contacts.html')
