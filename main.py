from gurobipy import *

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
    "12am": 3,
    "1am": 3,
    "2am": 3,
    "3am": 3,
    "4am": 3,
    "5am": 3,
    "6am": 3,
    "7am": 3,
    "8am": 3,
    "9am": 3,
    "10am": 3,
    "11am": 3})

A = [[1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
availability = {(w,s) : A[j][i] for i,s in enumerate(hourlyRequirements)
                                for j, w in enumerate(workers)}

# print(availability)

totHours = model.addVars(workers, name='TotHours')
# print(help(totHours['Madina']))
print(totHours[w].x <= maxHours[w] for w in workers)

# model.addConstr((totHours[w].x <= maxHours[w] for w in workers), name='maxHourRequirement')
#
# model.optimize()