# import random.randrange as rnrg
import random as rd
import numpy as np


def distance_between_points(pointA, pointB):
    return ((pointA[0]-pointB[0])**2+(pointA[1]-pointB[1])**2)**.5


def cost(permutation, num_cities, city_coordinates):
    cost = 0.0
    for i, point in enumerate(permutation):
        cost += (distance_between_points(city_coordinates[int(point)],
                 city_coordinates[int(permutation[i+1])])
                 if (i != num_cities-1) else
                 distance_between_points(city_coordinates[int(point)],
                 city_coordinates[int(permutation[0])]))
    return (permutation, cost)


def choose_next(cities_visited, city_coordinates, num_cities, pheremone_array):
    cities_visited = cities_visited.tolist()
    current_city = int(cities_visited[len(cities_visited)-1])
    x = 1
    while True:
        choices = []
        for i in range(num_cities):
            if i not in cities_visited:
                choice = {}
                choice["city_index"] = i
                choice["cost"] = (1.0/distance_between_points
                                  (city_coordinates[current_city],
                                   city_coordinates[i])) ** heuristic_coefficient
                choice["pheremones"] = (pheremone_array[current_city][i]
                                        ** history_coefficient)
                choice["chance"] = (choice["pheremones"] * choice["cost"]
                                    if choice["pheremones"] >= 0 else 0)
                choices.append(choice)
        try:
            return (rd.choices([v for sublist in choices for (k, v)
                    in sublist.items() if k == "city_index"],
                    [v for sublist in choices for (k, v)
                    in sublist.items() if k == "chance"])[0])
        except ValueError:
            choice["pheremones"] = ((pheremone_array[current_city][i]+x)
                                    ** history_coefficient)
            x += 1


def update_pheremones(pheremones, solutions, num_cities, city_coordinates):
    for solution in solutions:
        for iteration, city_index in enumerate(solution):
            second_city_index = (city_index + 1 if
                                 (iteration > num_cities - 1) else 0)
            pheremones[int(city_index)][int(second_city_index)] += (1.0/cost(solution, num_cities, city_coordinates)[1])
            pheremones[int(second_city_index)][int(city_index)] += (1.0/cost(solution, num_cities, city_coordinates)[1])


berlin52 = [[565, 575], [25, 185], [345, 750], [945, 685], [845, 655],
            [880, 660], [25, 230], [525, 1000], [580, 1175], [650, 1130],
            [1605, 620], [1220, 580], [1465, 200], [1530, 5], [845, 680],
            [725, 370], [145, 665], [415, 635], [510, 875], [560, 365],
            [300, 465], [520, 585], [480, 415], [835, 625], [975, 580],
            [1215, 245], [1320, 315], [1250, 400], [660, 180], [410, 250],
            [420, 555], [575, 665], [1150, 1160], [700, 580], [685, 595],
            [685, 610], [770, 610], [795, 645], [720, 635], [760, 650],
            [475, 960], [95, 260], [875, 920], [700, 500], [555, 815],
            [830, 485], [1170, 65], [830, 610], [605, 625], [595, 360],
            [1340, 725], [1740, 245]]
city_coordinates = berlin52
num_cities = len(city_coordinates)
max_iterations = 20
num_ants = 100
decay_factor = .6
heuristic_coefficient = 3.0
history_coefficient = 2.0
meta_iterations = 0
meta_persistance_percentile = 0
meta_persistence_rounds = 0


def find_path(pheremones=None, best=None, max_iterations=max_iterations):
    if pheremones is None:
        # create a naive pheremone array
        pheremones = np.ones((num_cities, num_cities))
    # create a naive permutation, set to best
    temp = []
    for i in range(num_cities):
        temp.append(i)
    if best is None:
        best = cost(rd.sample(temp, num_cities), num_cities, city_coordinates)
    # start a number of iterations:
    # for _ in range(max_iterations):
    for _ in range(max_iterations):
        # move each ant 1 movement
        solutions = np.zeros((num_ants, num_cities))
        temp = rd.sample(temp, num_cities)
        for i in range(num_ants):
            solutions[i, 0] = temp[i % num_cities]
        for num_cities_travelled in range(1, num_cities):
            for i in range(num_ants):
                solutions[i, num_cities_travelled] = (choose_next(solutions[i]
                                                      [0:num_cities_travelled],
                                                      city_coordinates,
                                                      num_cities, pheremones))
        # update best solution, if better solution found
        for solution in solutions:
            if cost(solution, num_cities, city_coordinates)[1] < best[1]:
                best = cost(solution, num_cities, city_coordinates)
                print(best[1])
        # decay and update pheremones
        pheremones *= (1.0 - decay_factor)
        update_pheremones(pheremones, solutions, num_cities, city_coordinates)
    # run next iteration
    return (best, pheremones)


best_solutions = []
best_solutions.append(find_path())
for _ in range(meta_iterations):
    temp = find_path()
    for i in range(len(best_solutions)):
        if (temp[0][1] > best_solutions[i][0][1]):
            best_solutions.insert(i, temp)
for r in range(meta_persistence_rounds):
    print("entering round: %a" % r)
    _ls = best_solutions[int(len(best_solutions)*meta_persistance_percentile):]
    old_solutions = _ls if len(_ls) > 0 else best_solutions[-1:]
    best_solutions = []
    best_solutions.append(find_path(old_solutions[0][1], old_solutions[0][0]))
    for i in range(1, len(old_solutions)):
        temp = find_path(old_solutions[i][1], old_solutions[i][0])
        for i in range(len(best_solutions)):
            if (temp[0][1] > best_solutions[i][0][1]):
                best_solutions.insert(i, temp)
print("best path was %a units long." % best_solutions[-1][0][1])
