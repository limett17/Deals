from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.bitrix_token import BitrixToken
from products.utils.webhook import web_hook_auth, domain
from datetime import datetime, timedelta, timezone


@main_auth(on_cookies=True)
def list_people(request):
    webhook_token = BitrixToken(
        web_hook_auth=web_hook_auth,
        domain=domain,
    )
    # получаю список всех отделов
    departments = webhook_token.call_api_method('department.get', params={}).get("result", {})
    # print(departments)

    # получаю список всех работников по отделам
    dep_ids = []
    for department in departments:
        department_id = department.get("ID")
        dep_ids.append(department_id)
    employees_by_dep = webhook_token.call_api_method('im.department.employees.get', params={
        "ID": dep_ids,
        "USER_DATA": "Y",
        }).get("result", {})
    # print(employees_by_dep)
    # список руководителей всех отделов
    managers_by_dep = webhook_token.call_api_method('im.department.managers.get', params={
        "ID": dep_ids,
        "USER_DATA": "Y",
    }).get("result", {})
    # print(managers_by_dep)

    # получаю исходящие звонки за последние сутки продолжительностью более 60 сек
    now = datetime.now(timezone(timedelta(hours=3)))
    since = now - timedelta(hours=24)

    since_iso = since.isoformat()

    calls = webhook_token.call_api_method('voximplant.statistic.get', {
        'FILTER': {
            'CALL_TYPE': '1',
            '>CALL_DURATION': 60,
            '>CALL_START_DATE': since_iso
        }
    }).get("result", {})


    def build_department_tree(departments):
        parent_map = {}
        name_map = {}
        for dep in departments:
            dep_id = dep['ID']
            parent_id = dep.get('PARENT')
            parent_map[dep_id] = parent_id
            name_map[dep_id] = dep['NAME']
        return parent_map, name_map

    def build_user_map(employees_by_dep):
        user_map = {}
        for users in employees_by_dep.values():
            for user in users:
                user_map[str(user['id'])] = user
        return user_map

    def get_leader_chain(dep_id, parent_map, managers_by_dep, employee_id):
        chain = []
        current = dep_id
        while current:
            managers = managers_by_dep.get(current, [])
            for m in managers:
                if str(m['id']) != str(employee_id):
                    chain.append({'id': m['id'], 'name': m['name']})
            current = parent_map.get(current)
        return chain

    def count_calls(calls):
        counter = {}
        for call in calls:
            user_id = str(call.get('PORTAL_USER_ID'))
            if user_id in counter:
                counter[user_id] += 1
            else:
                counter[user_id] = 1
        return counter

    def build_table_rows(departments, employees_by_dep, managers_by_dep):
        parent_map, dep_name_map = build_department_tree(departments)
        user_map = build_user_map(employees_by_dep)


        rows = []
        max_depth = 0
        calls_count = count_calls(calls)
        for dep_id, employees in employees_by_dep.items():
            for emp in employees:
                if not emp.get("active"):
                    continue

                emp_id = str(emp["id"])

                emp_name = emp["name"]
                chain = get_leader_chain(dep_id, parent_map, managers_by_dep, emp_id)
                max_depth = max(max_depth, len(chain))

                callcount = calls_count.get(emp_id)

                rows.append({
                    "employee_id": emp_id,
                    "employee_name": emp_name,
                    "department_id": dep_id,
                    "department_name": dep_name_map.get(dep_id, f"Отдел {dep_id}"),
                    "leader_chain": chain,
                    "calls_count": callcount,
                })

        return rows, max_depth

    table_rows, max_leader_depth = build_table_rows(departments, employees_by_dep, managers_by_dep)
    leader_indices = range(max_leader_depth)

    for row in table_rows:
        chain = row['leader_chain']
        padded_chain = chain + [None] * (max_leader_depth - len(chain))
        row['leader_chain'] = padded_chain

    return render(request, 'list_people.html', {
        "table_rows": table_rows,
        "leader_indices": leader_indices,
    })
