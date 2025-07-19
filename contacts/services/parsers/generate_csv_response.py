import csv
from django.http import HttpResponse
from io import StringIO


def generate_csv_response(data, filename="contacts.csv"):
    buffer = StringIO()

    buffer.write('\ufeff')

    writer = csv.writer(buffer, delimiter=',')

    writer.writerow(["имя", "фамилия", "телефон", "email", "компания"])

    for item in data:
        writer.writerow([
            item.get("имя", ""),
            item.get("фамилия", ""),
            item.get("телефон", ""),
            item.get("email", ""),
            item.get("компания", "")
        ])

    response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response