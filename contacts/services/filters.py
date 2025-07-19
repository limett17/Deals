from datetime import datetime


def build_contact_filters_from_request(request, company_id):
    filters = {}
    export_date_from = request.POST.get('export_date_from')
    export_date_to = request.POST.get('export_date_to')
    only_phone_number = request.POST.get('only_phone_number')
    only_email = request.POST.get('only_email')
    if company_id:
        filters['COMPANY_ID'] = company_id

    if export_date_from:
        try:
            date_from = datetime.strptime(export_date_from, "%Y-%m-%d")
            filters[">=DATE_CREATE"] = date_from.strftime("%Y-%m-%dT00:00:00")
        except ValueError:
            pass

    if export_date_to:
        print(export_date_to)
        try:
            date_to = datetime.strptime(export_date_to, "%Y-%m-%d")
            print(date_to)
            filters["<=DATE_CREATE"] = date_to.strftime("%Y-%m-%dT23:59:59")
        except ValueError:
            pass

    if only_phone_number:
        filters["HAS_PHONE"] = "Y"

    if only_email:
        filters["HAS_EMAIL"] = "Y"

    return filters
