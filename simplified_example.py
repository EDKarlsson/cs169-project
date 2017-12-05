from main import schedule_workers

pay = {
    "Madina": 10,
    "Alan": 12,
    "Ben": 10,
    "Dan": 8,
}

availability = {
    "Madina": [1, 1, 1, 1, 1, 1, 1],
    "Alan": [1, 1, 1, 1, 1, 1, 1],
    "Ben": [1, 1, 1, 1, 1, 1, 1],
    "Dan": [1, 1, 1, 1, 1, 1, 1]
}

roles = ['cashier', 'manager']
worker_roles = {
    "Madina": ['cashier'],
    "Alan": ['manager', 'cashier'],
    "Ben": ['cashier', 'manager'],
    "Dan": ['manager']
}


schedule_workers(pay, availability, roles, worker_roles,total_hours_in_day=5,max_hours_per_employee_per_day=3,total_days=3)