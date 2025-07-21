from integration_utils.bitrix24.functions import batch_api_call
from integration_utils.bitrix24.functions.batch_api_call import _batch_api_call

# кэш для компаний
company_cache = {}  # ключ: название компании, значение: ID


# эта функция используется при импорте для создания компании
# для контакта, если она указана в файле
def get_or_create_company_id(but, title):
    title = title.strip()

    # проверяем, если ли компания в кэше
    if title in company_cache:
        return company_cache[title]

    # не нашли - ищем в битриксе и получаем ID
    search_result = but.call_api_method("crm.company.list", {
        "filter": {"TITLE": title},
        "select": ["ID"]
    })

    # если нашли - сохраняем, если нет - создаем новую и получаем ее ID
    companies = search_result.get('result', [])
    if companies:
        company_id = companies[0]["ID"]
    else:
        create_result = but.call_api_method("crm.company.add", {
            "fields": {"TITLE": title}
        })
        company_id = create_result.get('result')

    # сохраняем созданную/найденную компанию в кэш
    company_cache[title] = company_id
    return company_id


# функция поиска дубликатов
def find_duplicate_contact_id(but, phone=None, email=None):
    contact_ids = set()

    if phone:
        res = but.call_api_method("crm.duplicate.findbycomm", {
            "type": "PHONE",
            "values": [phone],
            "entity_type": "CONTACT"
        })
        if res.get('result'):
            contact_ids.update(res.get("result", {}).get("CONTACT", []))

    if email:
        res = but.call_api_method("crm.duplicate.findbycomm", {
            "type": "EMAIL",
            "values": [email],
            "entity_type": "CONTACT"
        })
        if res.get('result'):
            contact_ids.update(res.get("result", {}).get("CONTACT", []))

    return list(contact_ids)


# получение контакта по id
def get_contact_by_id(but, contact_id):
    res = but.call_api_method("crm.contact.get", {"id": contact_id})
    return res.get("result")


def batch_create_contacts(but, contacts_generator, chunk_size=50):
    batch = []
    successes = []
    errors = []

    for i, contact in enumerate(contacts_generator):
        if not contact.get("PHONE") and not contact.get("EMAIL"):
            continue

        phone = contact["PHONE"][0]["VALUE"] if contact.get("PHONE") else None
        email = contact["EMAIL"][0]["VALUE"] if contact.get("EMAIL") else None

        duplicate_ids = find_duplicate_contact_id(but, phone, email)
        is_duplicate = False

        for dup_id in duplicate_ids:
            existing = get_contact_by_id(but, dup_id)
            if existing:
                same_name = existing.get("NAME", "").strip() == contact.get("NAME", "").strip()
                same_last_name = existing.get("LAST_NAME", "").strip() == contact.get("LAST_NAME", "").strip()

                existing_company_id = existing.get("COMPANY_ID")
                existing_company_title = ""
                if existing_company_id:
                    company = but.call_api_method("crm.company.get", {"id": existing_company_id})
                    existing_company_title = company.get("result", {}).get("TITLE", "").strip()

                same_company = existing_company_title == contact.get("COMPANY_TITLE", "").strip()

                if same_name and same_last_name and same_company:
                    is_duplicate = True
                    break

        if is_duplicate:
            print('Такой контакт уже существует')
            continue

        fields = {
            "NAME": contact.get("NAME", ""),
            "LAST_NAME": contact.get("LAST_NAME", ""),
            "PHONE": contact.get("PHONE", []),
            "EMAIL": contact.get("EMAIL", [])
        }

        title = contact.get("COMPANY_TITLE")
        if title and title.strip():
            company_id = get_or_create_company_id(but, title)
            if company_id:
                fields["COMPANY_ID"] = company_id

        batch.append((
            f"contact_{i}",
            "crm.contact.add",
            {"fields": fields}
        ))

        if len(batch) >= chunk_size:
            result = _batch_api_call(
                methods=batch,
                bitrix_user_token=but,
                function_calling_from_bitrix_user_token_think_before_use=True,
                chunk_size=chunk_size
            )
            for call_key, call_result in result.items():
                if "error" in call_result:
                    errors.append({"key": call_key, "error": call_result["error"]})
                else:
                    successes.append(call_result["result"])
            batch.clear()

    if batch:
        result = _batch_api_call(
            methods=batch,
            bitrix_user_token=but,
            function_calling_from_bitrix_user_token_think_before_use=True,
            chunk_size=chunk_size
        )
        for call_key, call_result in result.items():
            if "error" in call_result:
                errors.append({"key": call_key, "error": call_result["error"]})
            else:
                successes.append(call_result["result"])

        return successes, errors
    return successes, errors

def stream_contacts(but, filters):
    start = 0
    company_cache = {}

    while True:
        res = but.call_api_method("crm.contact.list", {
            "filter": filters,
            "select": ["ID", "NAME", "LAST_NAME", "EMAIL", "PHONE", "COMPANY_ID"],
            "start": start
        })

        batch = res.get("result", [])
        if not batch:
            break

        for contact in batch:
            company_id = contact.get("COMPANY_ID")
            company_name = ""

            if company_id:
                if company_id in company_cache:
                    company_name = company_cache[company_id]
                else:
                    company = but.call_api_method("crm.company.get", {"id": company_id}).get("result")
                    company_name = company.get("TITLE", "") if company else ""
                    company_cache[company_id] = company_name

            yield {
                "имя": contact.get("NAME", ""),
                "фамилия": contact.get("LAST_NAME", ""),
                "номер телефона": contact.get("PHONE", [{}])[0].get("VALUE", "") if contact.get("PHONE") else "",
                "email": contact.get("EMAIL", [{}])[0].get("VALUE", "") if contact.get("EMAIL") else "",
                "компания": company_name
            }

        if "next" in res:
            start = res["next"]
        else:
            break


# эта функция используется при экпорте для проверки наличия
# введенной пользователем компании и звонков у нее
def get_company_id_if_exists(but, company_name):
    companies = but.call_api_method("crm.company.list", {
        "filter": {"TITLE": company_name},
        "select": ["ID"]
    })["result"]

    if not companies:
        return None

    company_id = companies[0]["ID"]

    contacts = but.call_api_method("crm.contact.list", {
        "filter": {"COMPANY_ID": company_id},
        "select": ["ID"],
        "limit": 1
    })["result"]

    if not contacts:
        return None

    return company_id
