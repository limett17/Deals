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
