from gurobipy import *
import numpy as np


def feasibility_checks(n,m, max_hours, A, roles, workers, worker_roles):
    """
    Does basic checks for feasibility for the given input.
    Note that these checks are not comprehensive and are just meant to catch simpler mistakes in the model setup.
    """
    days = [day for day in range(7)]
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # each role can be filled:
    for role in roles:
        role_filled = False
        for worker, allowed_roles in worker_roles.iteritems():
            if role in allowed_roles:
                role_filled = True
                continue
        assert role_filled, 'No employees can perform role: ' + role

    for day, avails in enumerate(A.T):
        assert sum(avails) >= len(roles), day_names[day] + ' does not have enough employees scheduled to fill all roles'

    for day, avails in enumerate(A.T):
        for role in roles:
            role_filled = False
            for i, avail in enumerate(avails):
                if role in worker_roles[workers[i]]:
                    role_filled = True
                    continue
            assert role_filled, 'Nobody can perform role: ' + role + ' on day: ' + day_names[day]

    assert m <= n * max_hours / len(roles), 'Not enough employees to fill each role every day'




def schedule_employees(pay, availability, roles, worker_roles):
    """
    example input:
    pay = {
        "Madina": 10,
        "Alan": 12,
        "Ben": 10,
        "Dan": 8
    }
    availability = {
        "Madina": [0, 1, 0, 1, 0, 1, 1],
        "Alan": [1, 0, 1, 0, 1, 1, 1],
        "Ben": [1, 1, 1, 1, 1, 0, 0],
        "Dan": [0, 1, 0, 1, 0, 0, 0]
    }
    roles = ['cashier', 'manager']
    worker_roles = {
        "Madina": ['manager'],
        "Alan": ['manager', 'cashier],
        "Ben": ['cashier'],
        "Dan": ['cashier']
    }

    :param pay: maps employees to pay
    :param availability: maps each employee to a list of binary values signifying availability per shift
    :param roles: list the necessary roles
    :param worker_roles: maps workers to the roles they can fullfill
    :return: resulting matrix of schedulings
    """


    model = Model('model')

    workers = pay.keys()

    n = len(pay)  # number of employees
    m = 12  # number hours in the day
    max_hours = 8

    days = [day for day in range(7)]
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    pay_vec = np.array([pay[worker] for worker in workers]) # pay vector
    A = np.array([[av for av in availability[worker]] for worker in workers]) # availability matrix

    feasibility_checks(n, m, max_hours, A, roles, workers, worker_roles)

    # form: hours[day][role][employee_index, hour_index]
    hours = [{role: np.array([[model.addVar(vtype=GRB.BINARY, name=role + '_x_{' + str(i) + ',' + str(j) + '}') for j in range(m)] for i in range(n)])
             for role in roles}
             for day in days]

    # worker can only work on days they're available
    for role in roles:
        for i in range(n):
            for day in days:
                for j in range(m):
                    if A[i, day] == 0:
                        model.addConstr(hours[day][role][i, j] == 0)

    # only one per shift per role
    for day in days:
        for role in roles:
            for col in hours[day][role].T:
                model.addConstr(quicksum(col) == 1)

    # all 12 shifts covered
    for day in days:
        for role in roles:
            model.addConstr(quicksum(hours[day][role].ravel()) >= m)

    # everyone can work a max of 8 hours per day
    for day in days:
            for row in sum(hours[day][role] for role in roles):
                model.addConstr(quicksum(row) <= max_hours)

    # each person can only perform only 1 role per day
    for day in days:
        for i in range(n):
            for j in range(m):
                for role in roles:
                    for other_role in roles:
                        if other_role != role:
                            model.addConstr((hours[day][role][i,j] == 1) >> (quicksum(hours[day][other_role][i,:]) == 0))

    # workers can only perform roles they're allowed to
    for role in roles:
        for i, worker in enumerate(workers):
            if role not in worker_roles[worker]:
                for day in days:
                    model.addConstr(quicksum(hours[day][role][i,:]) == 0)

    # shifts must be contiguous
    for day in days:
        for role in roles:
            for i in range(n):
                for j in range(m - 1):
                    # we want (hours[i,j] == 0 and (hours[i,j + 1] == 0 or quicksum(hours[i,:j]) == 0))
                    #          or hours[i,j] == 1) but we cant explicitly program logical constraints
                    helper = model.addVar(name='helper_{' + role + ',' + str(i) + ',' + str(j) + '}')
                    model.addConstr(helper == hours[day][role][i, j + 1] * quicksum(hours[day][role][i, :j]))  # if helper == 0 then either hours[i,j+1] is zero or all the previous hours are zero
                    model.addConstr((hours[day][role][i, j] == 0) >> (helper == 0))  # if hour j is a zero then hour j+1 can only be a 1 if all the previous are zero

    model.setObjective(quicksum(np.array(np.array([[np.dot(hours[day][role].T, pay_vec).ravel() for role in roles] for day in days]).ravel()).ravel()), GRB.MINIMIZE)

    model.update()
    model.optimize()

    while model.status == GRB.status.INFEASIBLE:
        model.feasRelaxS(1, True, False, True)
        model.update()
        model.optimize()
        print("Had infeasible model: relaxing constraints")

    # print binary matrix of role assignments
    # for day, day_name in enumerate(day_names):
    #     print '\n-----------------' + day_name + '---------------------\n'
    #     for k,role in enumerate(roles):
    #         print(role + ':')
    #         for i in range(n):
    #             print '    ' + workers[i] + ': [',
    #             for j in range(m):
    #                 print str(hours[day][role][i,j].X),
    #             print(']')

    # print a matrix of employee names
    for day, day_name in enumerate(day_names):
        print '\n-----------------' + day_name + '---------------------\n'
        for k, role in enumerate(roles):
            print role + ': [',
            for j in range(m):
                for i in range(n):
                    if hours[day][role][i,j].X == 1:
                        print str(j) + ' ' + workers[i] + ', ',
            print ']'

    model.write('main.lp')



if __name__ == '__main__':

    '''
    Note: we must have enough employees available to fill all the roles every day.

    i.e.
       employees_available_each_day ==  #_roles * (total_hours_in_day / max_hours_allowed_per_day)
    '''

    pay = {
        "Madina": 10,
        "Alan": 12,
        "Ben": 10,
        "Dan": 8,
        "Jack": 10,
        "Jill": 9,
        "Erik": 11,
        "Mjolsness": 14,
        "bob": 12,
        "sally": 13
    }

    # availability = {
    #     "Madina": [0, 1, 0, 1, 0, 1, 1],
    #     "Alan": [1, 0, 1, 0, 1, 1, 1],
    #     "Ben": [1, 1, 1, 1, 1, 0, 0],
    #     "Dan": [0, 1, 0, 1, 0, 0, 0],
    #     "Jack": [1, 1, 1, 1, 1, 1, 1],
    #     "Jill": [1, 1, 1, 1, 1, 1, 1],
    #     "Erik": [1, 1, 0, 0, 1, 1, 0],
    #     "Mjolsness": [1, 0, 1, 1, 0, 0,1 ],
    # }

    availability = {
        "Madina": [1, 0, 1, 0, 1, 1, 1],
        "Alan": [0, 1, 0, 1, 1, 1, 1],
        "Ben": [1, 1, 1, 1, 1, 0, 0],
        "Dan": [1, 1, 1, 1, 0, 1, 1],
        "Jack": [1, 1, 1, 1, 1, 1, 1],
        "Jill": [1, 1, 1, 1, 0, 1, 1],
        "Erik": [1, 1, 1, 1, 1, 1, 1],
        "Mjolsness": [1, 0, 1, 1, 1, 1, 1],
        "bob": [1, 1, 1, 1, 1, 1, 1],
        "sally": [0, 1, 1, 0, 0, 1, 1]
    }

    roles = ['cashier', 'manager', 'floor']
    worker_roles = {
        "Madina": ['cashier', 'floor', 'butcher'],
        "Alan": ['manager', 'cashier', 'floor'],
        "Ben": ['cashier', 'floor', 'manager'],
        "Dan": ['butcher', 'manager'],
        "Jack": ['cashier', 'floor', 'butcher'],
        "Jill": ['floor', 'cashier'],
        "Erik": ['cashier', 'floor', 'butcher'],
        "Mjolsness": ['manager', 'cashier'],
        "bob": ["cashier", "floor", "butcher"],
        "sally": ['cashier', 'floor', 'manager']
    }


    schedule_employees(pay, availability, roles, worker_roles)
