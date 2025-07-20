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


def generate_csv_response_from_stream(data_generator, filename="contacts.csv"):
    from django.http import StreamingHttpResponse
    import csv

    class Echo:
        def write(self, value):
            return value

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=',')

    def row_gen():
        yield '\ufeff'
        yield writer.writerow(["имя", "фамилия", "номер телефона", "email", "компания"])
        for row in data_generator:
            yield writer.writerow([
                row["имя"], row["фамилия"], row["номер телефона"], row["email"], row["компания"]
            ])

    response = StreamingHttpResponse(row_gen(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
