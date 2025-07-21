from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from contacts.services.filters import build_contact_filters_from_request
# from contacts.services.parsers.generate_csv_response import generate_csv_response
# from contacts.services.parsers.generate_xlsx_response import generate_xlsx_response
from contacts.services.bitrix import stream_contacts
from contacts.services.parsers.generate_csv_response import generate_csv_response_from_stream
from contacts.services.parsers.generate_xlsx_response import generate_xlsx_response_from_stream
from contacts.services.bitrix import get_company_id_if_exists


@main_auth(on_cookies=True)
def export_contacts(request):
    but = request.bitrix_user_token

    if request.method == 'POST':
        company_name = request.POST.get("company_name")
        company_id = None
        file_type = request.POST.get("export_format", "csv").lower()

        if company_name:
            company_id = get_company_id_if_exists(but, company_name)
            if company_id is None:
                return render(request, 'export_contacts.html', {
                    "error": "Компания не найдена или у нее нет контактов"
                })
        filters = build_contact_filters_from_request(request, company_id)
        # contacts = but.call_list_method("crm.contact.list", {
        #     "filter": filters,
        #     "select": ["ID", "NAME", "LAST_NAME", "EMAIL", "PHONE", "COMPANY_ID"],
        #     "start": 0
        # })["result"]
        contact_generator = stream_contacts(but, filters)

        if file_type == "xlsx":
            # contact_list = list(contact_generator)
            # return generate_xlsx_response(contact_list)
            return generate_xlsx_response_from_stream(contact_generator)
        else:
            return generate_csv_response_from_stream(contact_generator)

        # if not contacts:
        #     return render(request, 'export_contacts.html', {
        #         "error": "Контакты не найдены по заданным условиям"
        #     })
        #
        # contact_list = create_contact_list(contacts, but)
        #
        # if file_type == "xlsx":
        #     return generate_xlsx_response(contact_list)
        # else:
        #     return generate_csv_response(contact_list)
    return render(request, 'export_contacts.html')
