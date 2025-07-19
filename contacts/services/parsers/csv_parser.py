import csv
from io import TextIOWrapper


def parse_csv(file):
    reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
    # файл читается как список словарей и конвертируется в текст (?)
    return [
        {
            'NAME': row['имя'],
            'LAST_NAME': row['фамилия'],
            'PHONE': [{'VALUE': row['номер телефона'], 'VALUE_TYPE': 'WORK'}],
            'EMAIL': [{'VALUE': row['почта'], 'VALUE_TYPE': 'WORK'}],
            'COMPANY_TITLE': row['компания']
        }
        for row in reader
    ]
