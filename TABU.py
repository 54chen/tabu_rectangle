import argparse
from re import S
from tempfile import tempdir
import time
import pandas as pd
import copy
from BLF import BLF
import random

##
# ##
##
SCOPE=20
RESOLUTION=1

def fitness(solution):
    temp = copy.deepcopy(solution)
    temp["x"] = 0
    temp["y"] = 0
    temp["status"] = 0
    blf = BLF(temp, SCOPE, RESOLUTION)
    blf.run()
    value = blf.length
    return temp,value

def generate_first_solution(csv):
    print("start to generate first solution...")
    header_list = ["id", "width", "height"]
    rectangles = pd.read_csv(csv, names=header_list, skipfooter=1, engine='python')
    rectangles["x"] = 0
    rectangles["y"] = 0
    rectangles["status"] = 0
    rectangles["vertical"] = 0

    return fitness(rectangles)

def find_neighborhood(solution):
    s = copy.deepcopy(solution)

    neighborhood_of_solution = []

    for n in range(len(s)):
        idx1 = s.iloc[n].copy()
        for m in range(len(s)):
            idx2 = s.iloc[m].copy()
            if m == n:
                continue
            mem = copy.deepcopy(s)
            mem.iloc[m] = idx1
            mem.iloc[n] = idx2  
            neighborhood_of_solution.append(mem)

    for n in range(len(s)):
        width = solution.iloc[n]["width"]
        height = solution.iloc[n]["height"]
        mem2 = copy.deepcopy(solution)
        mem2.iloc[n]["width"] = height
        mem2.iloc[n]["height"] = width
        mem2.iloc[n]["vertical"] = 1
        neighborhood_of_solution.append(mem2)

    for n in range(len(mem2)):
        idx1 = mem2.iloc[n].copy()
        for m in range(len(s)):
            idx2 = s.iloc[m].copy()
            if m == n:
                continue
            mem3 = copy.deepcopy(s)
            mem3.iloc[m] = idx1
            mem3.iloc[n] = idx2
            neighborhood_of_solution.append(mem3)

    random.shuffle(neighborhood_of_solution)
    return neighborhood_of_solution

def tabu_search(first_solution, value, iters, size):
    count = 1
    solution = copy.deepcopy(first_solution)
    tabu_list = list()
    best_value = value
    best_solution_ever = solution
    while count <= iters:
        neighborhood = find_neighborhood(solution)
        index_of_best_solution = 0 
        best_solution = neighborhood[index_of_best_solution]

        found = False
        while not found:
            i = 0

            first_exchange_node = "1_0"
            second_exchange_node = "2_0"
            while i < len(best_solution):
                if best_solution.iloc[i]["id"] != solution.iloc[i]["id"] or (best_solution.iloc[i]["id"] == solution.iloc[i]["id"] and best_solution.iloc[i]["vertical"] != solution.iloc[i]["vertical"]):
                    first_exchange_node = str(best_solution.iloc[i]["id"])+"_"+str(best_solution.iloc[i]["vertical"])
                    second_exchange_node = str(solution.iloc[i]["id"])+"_"+str(solution.iloc[i]["vertical"])
                    break
                i = i + 1

            if [first_exchange_node, second_exchange_node] not in tabu_list and [
                second_exchange_node, first_exchange_node] not in tabu_list:

                tabu_list.append([first_exchange_node, second_exchange_node])
                found = True
                solution = best_solution
                temp,length = fitness(neighborhood[index_of_best_solution])
                print("iters: %d fitness result: %d" % (count, length))

                if length < best_value:
                    best_value = length
                    best_solution_ever = temp
            else:
                print("iters: %d fitness result: %d. find in tabu list" % (count, length))
                index_of_best_solution = index_of_best_solution + 1
                best_solution = neighborhood[index_of_best_solution]
        if len(tabu_list) >= size:
            tabu_list.pop(0)

        count = count + 1

    return best_solution_ever, best_value
    
def main(args=None):
    start = time.perf_counter()
    first_solution, value = generate_first_solution(args.File)

    best_sol, best_value = tabu_search(
        first_solution,
        value,
        args.Iterations,
        args.Size,
    )
    print(f"Best solution: \n{best_sol}, \n with total length: {best_value}.")
    end = time.perf_counter()
    print("[time cost] " + str(end-start) + "s")
    BLF.showResult(best_sol, 100, best_value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tabu Search")
    parser.add_argument(
        "-f",
        "--File",
        type=str,
        help="Path to the file containing the data",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--Iterations",
        type=int,
        help="How many iterations the algorithm should perform",
        required=True,
    )
    parser.add_argument(
        "-s", "--Size", type=int, help="Size of the tabu list", required=True
    )

    # Pass the arguments to main method
    main(parser.parse_args())
    
