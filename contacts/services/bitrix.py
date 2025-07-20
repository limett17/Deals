from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.bitrix_token import BitrixToken
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


def batch_create_contacts(but, contacts_generator, chunk_size=50):
    batch = []
    successes = []
    errors = []

    for i, contact in enumerate(contacts_generator):
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
