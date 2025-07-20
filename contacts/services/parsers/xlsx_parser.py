import openpyxl


def parse_xlsx(file):
    wb = openpyxl.load_workbook(file, read_only=True)
    ws = wb.active

    rows = ws.iter_rows(values_only=True)
    headers = next(rows)

    normalized_headers = [str(h).strip().lower() if h else "" for h in headers]

    idx = {
        "имя": normalized_headers.index("имя") if "имя" in normalized_headers else None,
        "фамилия": normalized_headers.index("фамилия") if "фамилия" in normalized_headers else None,
        "номер телефона": normalized_headers.index("номер телефона") if "номер телефона" in normalized_headers else None,
        "почта": normalized_headers.index("почта") if "почта" in normalized_headers else None,
        "компания": normalized_headers.index("компания") if "компания" in normalized_headers else None,
    }

    for row in rows:
        if not any(row):
            continue  # пропускаем пустые строки

        def safe_get(i):
            return (row[i] if i is not None and i < len(row) else "") or ""

        yield {
            "NAME": str(safe_get(idx["имя"])).strip(),
            "LAST_NAME": str(safe_get(idx["фамилия"])).strip(),
            "PHONE": [{"VALUE": str(safe_get(idx["номер телефона"])).strip(), "VALUE_TYPE": "WORK"}],
            "EMAIL": [{"VALUE": str(safe_get(idx["почта"])).strip(), "VALUE_TYPE": "WORK"}],
            "COMPANY_TITLE": str(safe_get(idx["компания"])).strip()
        }

