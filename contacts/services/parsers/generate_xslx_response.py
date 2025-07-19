from openpyxl import Workbook
from django.http import HttpResponse
from io import BytesIO


def generate_xlsx_response(data, filename="contacts.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Контакты"

    ws.append(list(data[0].keys()))

    for row in data:
        ws.append(list(row.values()))

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
