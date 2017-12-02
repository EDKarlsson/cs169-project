from gurobipy import *
import numpy as np

# Gurobi Model
model = Model("Assignment")

MIN_HOURS = 4

# Workers, Pay per hour and max number of hours available to work per day.
workers, pay, maxHours = multidict({
    "Madina": [10, 6],
    "Alan": [12, 8],
    "Ben": [10, 5],
    "Dan": [8, 12]})

# Work hours and number of workers required per hour
workHours, hourlyRequirements = multidict({
    "mam": 3,
    "1am": 3,
    "2am": 3,
    "3am": 3,
    "nam": 3,
    "5am": 3,
    "6am": 3,
    "7am": 3,
    "8am": 3,
    "9am": 3,
    "10am": 3,
    "11am": 3})

n = 4
m = 12

A = np.array([[1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

pay_vec = np.array([pay[worker] for worker in workers])

print(pay_vec)

hours = np.array([[model.addVar(vtype=GRB.BINARY,name='x_{' + str(i) + ',' + str(j) + '}') for j in range(m)] for i in range(n)])
removable_constrs = []
for i in range(n):
    for j in range(m):
        if A[i,j] == 0:
            model.addConstr(hours[i,j] == 0)


for col in hours.T:
    model.addConstr(quicksum(col) == 1) # only one per shift

model.addConstr(quicksum(hours.ravel()) >= m) # all 12 shifts covered

row_max_hours = [2 for row in hours]
for i,row in enumerate(hours):
    removable_constrs.append(model.addConstr(quicksum(row) <= row_max_hours[i], name=str(i))) # only 3 hour shifts allowed per person

for i in range(n):
    for j in range(m - 1):
        # we want (hours[i,j] == 0 and (hours[i,j + 1] == 0 or quicksum(hours[i,:j]) == 0))
        #          or hours[i,j] == 1) but we cant explicitly program logical constraints
        helper = model.addVar()
        model.addConstr(helper == hours[i,j + 1] * quicksum(hours[i,:j])) # if helper == 0 then either hours[i,j+1] is zero or all the previous hours are zero
        model.addConstr((hours[i,j] == 0) >> (helper == 0)) # if hour j is a zero then hour j+1 can only be a 1 if all the previous are zero


model.setObjective(quicksum(np.dot(hours.T, pay_vec).ravel()), GRB.MINIMIZE)

model.update()
model.optimize()

removed = []


while model.status == GRB.status.INFEASIBLE:
    # model.computeIIS()
    model.feasRelaxS(1, True, False, True)
    model.update()
    model.optimize()

results = np.ndarray(shape=(n,m))
for i in range(n):
    for j in range(m):
        results[i,j] = hours[i,j].X

for i,row in enumerate(results):
    print(workers[i],row)

# for i,row in enumerate(np.array(model.X).reshape(n,m)):
#     print(workers[i],row)

