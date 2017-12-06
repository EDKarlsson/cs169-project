from main import schedule_workers
import timeit
import matplotlib.pyplot as plt

pay = {
#     "Madina": 10
}

availability = {
    # "Madina": [1, 1, 0]
}

roles = ['cashier', 'manager']
worker_roles = {
    # "Madina": ['cashier','manager']
}

times = []

for i in range(100):
    worker = 'worker_' + str(i)
    pay[worker] = 10
    availability[worker] = [1,1,1]
    worker_roles[worker] = roles
    if i > 2:
        times.append(timeit.timeit(lambda: schedule_workers(pay, availability, roles, worker_roles,total_hours_in_day=5,max_hours_per_employee_per_day=3,total_days=3),number=10))

print(times)
plt.title("runtime")
plt.xlabel("number of workers")
plt.ylabel("runtime (in seconds)")
plt.plot(times)
plt.show()