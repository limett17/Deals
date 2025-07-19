import mimetypes
from contacts.services.parsers.csv_parser import parse_csv
from contacts.services.parsers.xlsx_parser import parse_xlsx
from contacts.services.bitrix import batch_create_contacts
from collections import namedtuple

ImportResult = namedtuple("ImportResult", ["successes", "errors", "all_ok"])


def import_contacts_from_file(but, uploaded_file):
    content_type = mimetypes.guess_type(uploaded_file.name)[0]

    if uploaded_file.name.endswith(".csv") or content_type == "text/csv":
        contacts = parse_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        contacts = parse_xlsx(uploaded_file)
    else:
        raise ValueError("Неподдерживаемый формат файла")

    result = batch_create_contacts(but, contacts)
    return result
