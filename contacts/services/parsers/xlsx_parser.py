import openpyxl


def parse_xlsx(file):
    wb = openpyxl.load_workbook(file)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    headers = [h.strip().lower() for h in rows[0]]
    data = rows[1:]

    result = []
    for row in data:
        record = dict(zip(headers, row))
        result.append({
            'NAME': record['имя'],
            'LAST_NAME': record['фамилия'],
            'PHONE': [{'VALUE': record['номер телефона'], 'VALUE_TYPE': 'WORK'}],
            'EMAIL': [{'VALUE': record['почта'], 'VALUE_TYPE': 'WORK'}],
            'COMPANY_TITLE': record['компания']
        })
    return result
