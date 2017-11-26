from gurobipy import *

# Gurobi Model
model = Model("Assignment")

MIN_HOURS = 4

# Workers, Pay per hour and max number of hours available to work per day.
workers, pay, maxHours = multidict({
    "Madina": [10, 6],
    "Alan": [12, 8],
    "Ben": [10, 5],
    "Dan": [8, 8]})

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

t_m = model.addVar(lb=MIN_HOURS, ub=8, name="madina_time_worked")
t_a = model.addVar(lb=MIN_HOURS, ub=8, name="alan_time_worked")
t_b = model.addVar(lb=MIN_HOURS, ub=8, name="ben_time_worked")
t_d = model.addVar(lb=MIN_HOURS, ub=8, name="dan_time_worked")

model.addConstr(t_m <= maxHours["Madina"], "madina_max_hour")
model.addConstr(t_a <= maxHours["Alan"], "alan_max_hour")
model.addConstr(t_b <= maxHours["Ben"], "ben_max_hour")
model.addConstr(t_d <= maxHours["Dan"], "dan_max_hour")

model.optimize()