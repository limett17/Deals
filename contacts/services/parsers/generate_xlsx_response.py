from openpyxl import Workbook
from django.http import HttpResponse
from io import BytesIO
import xlsxwriter


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


def generate_xlsx_response_from_stream(data_generator, filename="contacts.xlsx"):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Контакты")

    headers = ["имя", "фамилия", "номер телефона", "email", "компания"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    row_num = 1
    for item in data_generator:
        worksheet.write(row_num, 0, item.get("имя", ""))
        worksheet.write(row_num, 1, item.get("фамилия", ""))
        worksheet.write(row_num, 2, item.get("номер телефона", ""))
        worksheet.write(row_num, 3, item.get("email", ""))
        worksheet.write(row_num, 4, item.get("компания", ""))
        row_num += 1

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
