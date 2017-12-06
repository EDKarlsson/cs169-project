from main import schedule_workers
import timeit
import matplotlib.pyplot as plt
import numpy as np

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

varnum_to_runtime = []
with open('linedata.csv', 'w') as linedata:
    linedata.write('runtime, variablecount' + '\n')
    for i in range(50):
        for _ in range(10):
            try :
                worker = 'worker_' + str(i)
                pay[worker] = int(np.random.randint(1,20))
                total_days = 3
                total_hours_in_days = int(np.random.randint(1,i)) if i > 1 else 1
                availability[worker] = list(np.random.randint(0,2,total_days))#[1,1,1]
                max_hr_per_day = int(np.random.randint(total_hours_in_days / i, total_hours_in_days + 1)) if i > 0 else 1
                worker_roles[worker] = roles
                model = None

                def get_model():
                    global model
                    model = schedule_workers(pay, availability, roles, worker_roles, total_hours_in_day=total_hours_in_days,
                                             max_hours_per_employee_per_day=max_hr_per_day, total_days=total_days)
                if i > 2:
                    runtime = timeit.timeit(lambda: get_model(),number=1)
                    # times.append(runtime)
                    # varnum_to_runtime.append((runtime, len(model.getVars())))
                    linedata.write(str(runtime) + ',' + str(len(model.getVars())) + '\n')

            except AssertionError:
                pass # skip infeasible models

    # linedata.write('runtime, variablecount' + '\n')
    # for r,v in varnum_to_runtime:
    #     linedata.write(str(r) + ',' + str(v) + '\n')

print(times)
plt.title("runtime")
plt.xlabel("number of workers")
plt.ylabel("runtime (in seconds)")
plt.plot(times)
plt.show()