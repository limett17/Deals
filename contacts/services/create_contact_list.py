def create_contact_list(contacts, but):
    result = []
    company_cache = {}

    for contact in contacts:
        company_id = contact.get("COMPANY_ID")
        company_name = ""

        if company_id:
            if company_id in company_cache:
                company_name = company_cache[company_id]
            else:
                company = but.call_api_method("crm.company.get", {"id": company_id})['result']
                company_name = company.get("TITLE", "")
                company_cache[company_id] = company_name

        result.append({
            "имя": contact.get("NAME", ""),
            "фамилия": contact.get("LAST_NAME", ""),
            "номер телефона": contact.get("PHONE", [{}])[0].get("VALUE", "") if contact.get("PHONE") else "",
            "email": contact.get("EMAIL", [{}])[0].get("VALUE", "") if contact.get("EMAIL") else "",
            "компания": company_name
        })

    return result
