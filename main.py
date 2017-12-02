from gurobipy import *
import numpy as np


def schedule_employees(pay, availability):
    '''
    :param n: number of employees
    :param m: number of shifts
    :param pay: maps employees to pay
    :param availability: maps each employee to a list of binary values signifying availability per shift
    :return: resulting matrix of schedulings
    '''

    model = Model('model')

    workers = pay.keys()

    n = len(pay)
    m = len(availability[workers[0]])

    # for worker_1 in workers:
    #     for worker_2 in workers:
    #         assert len(worker_1[availability]) == len(worker_2[availability])

    pay_vec = np.array([pay[worker] for worker in workers])
    A = np.array([[av for av in availability[worker]] for worker in workers])

    print(A)

    hours = np.array(
        [[model.addVar(vtype=GRB.BINARY, name='x_{' + str(i) + ',' + str(j) + '}') for j in range(m)] for i in
         range(n)])

    removable_constrs = []
    for i in range(n):
        for j in range(m):
            if A[i, j] == 0:
                model.addConstr(hours[i, j] == 0)

    for col in hours.T:
        model.addConstr(quicksum(col) == 1)  # only one per shift

    model.addConstr(quicksum(hours.ravel()) >= m)  # all 12 shifts covered

    row_max_hours = [2 for row in hours]
    for i, row in enumerate(hours):
        removable_constrs.append(
            model.addConstr(quicksum(row) <= row_max_hours[i], name=str(i)))  # only 3 hour shifts allowed per person

    for i in range(n):
        for j in range(m - 1):
            # we want (hours[i,j] == 0 and (hours[i,j + 1] == 0 or quicksum(hours[i,:j]) == 0))
            #          or hours[i,j] == 1) but we cant explicitly program logical constraints
            helper = model.addVar(name='helper_{' + str(i) + ',' + str(j) + '}')
            model.addConstr(helper == hours[i, j + 1] * quicksum(
                hours[i, :j]))  # if helper == 0 then either hours[i,j+1] is zero or all the previous hours are zero
            model.addConstr((hours[i, j] == 0) >> (
            helper == 0))  # if hour j is a zero then hour j+1 can only be a 1 if all the previous are zero

    model.setObjective(quicksum(np.dot(hours.T, pay_vec).ravel()), GRB.MINIMIZE)

    model.update()
    model.optimize()

    removed = []

    while model.status == GRB.status.INFEASIBLE:
        # model.computeIIS()
        model.feasRelaxS(1, True, False, True)
        model.update()
        model.optimize()

    results = np.ndarray(shape=(n, m))
    for i in range(n):
        for j in range(m):
            results[i, j] = hours[i, j].X

    for i, row in enumerate(results):
        print(workers[i], row)

    # for i,row in enumerate(np.array(model.X).reshape(n,m)):
    #     print(workers[i],row)

    model.write('main.lp')


pay = {
    "Madina": 10,
    "Alan": 12,
    "Ben": 10,
    "Dan": 8
}

availability = {
    "Madina": [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    "Alan": [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    "Ben": [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    "Dan": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
}

schedule_employees(pay,availability)