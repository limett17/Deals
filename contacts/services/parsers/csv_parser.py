import csv
import io


def parse_csv(file):
    text = io.TextIOWrapper(file, encoding='utf-8')
    reader = csv.DictReader(text)

    for row in reader:
        yield {
            "NAME": row.get("имя", ""),
            "LAST_NAME": row.get("фамилия", ""),
            "PHONE": [{"VALUE": row.get("номер телефона", ""), "VALUE_TYPE": "WORK"}] if row.get("номер телефона") else [],
            "EMAIL": [{"VALUE": row.get("email", ""), "VALUE_TYPE": "WORK"}] if row.get("email") else [],
            "COMPANY_TITLE": row.get("компания", "")
        }
