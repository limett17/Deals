from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.bitrix_token import BitrixToken
from integration_utils.bitrix24.functions.batch_api_call import _batch_api_call

# кэш для компаний
company_cache = {}  # ключ: название компании, значение: ID


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


def batch_create_contacts(but, contacts, chunk_size=50):
    methods = []

    for i, contact in enumerate(contacts):
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

        methods.append((
            f"contact_{i}",
            "crm.contact.add",
            {"fields": fields}
        ))

    responses = _batch_api_call(
        methods=methods,
        bitrix_user_token=but,
        function_calling_from_bitrix_user_token_think_before_use=True,
        chunk_size=chunk_size
    )
    print(responses)
    return responses
