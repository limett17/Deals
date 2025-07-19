from django.shortcuts import render

from contacts.services.create_contact_list import create_contact_list
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from contacts.services.filters import build_contact_filters_from_request
from contacts.services.parsers.generate_csv_response import generate_csv_response
from contacts.services.parsers.generate_xslx_response import generate_xlsx_response


def get_company_id_if_exists(but, company_name):
    companies = but.call_api_method("crm.company.list", {
        "filter": {"TITLE": company_name},
        "select": ["ID"]
    })["result"]

    if not companies:
        return None

    company_id = companies[0]["ID"]

    contacts = but.call_api_method("crm.contact.list", {
        "filter": {"COMPANY_ID": company_id},
        "select": ["ID"],
        "limit": 1
    })["result"]

    if not contacts:
        return None

    return company_id


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
        contacts = but.call_api_method("crm.contact.list", {
            "filter": filters,
            "select": ["ID", "NAME", "LAST_NAME", "EMAIL", "PHONE", "COMPANY_ID"],
            "start": 0
        })["result"]

        if not contacts:
            return render(request, 'export_contacts.html', {
                "error": "Контакты не найдены по заданным условиям"
            })

        contact_list = create_contact_list(contacts, but)

        if file_type == "xlsx":
            return generate_xlsx_response(contact_list)
        else:
            return generate_csv_response(contact_list)
    return render(request, 'export_contacts.html')
