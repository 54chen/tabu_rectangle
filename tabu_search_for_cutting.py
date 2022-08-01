import argparse
import time
import pandas as pd
import copy
from BLF import BLF

##
# ##
##
SCOPE=20
RESOLUTION=1

def generate_first_solution(csv):
    header_list = ["id", "width", "height"]
    rectangles = pd.read_csv(csv, names=header_list, skipfooter=1, engine='python')
    rectangles["x"] = 0
    rectangles["y"] = 0
    rectangles["status"] = 0
    rectangles["vertical"] = 0

    blf = BLF(rectangles, SCOPE, RESOLUTION)
    blf.run()
    return rectangles, blf.length

def find_neighborhood(solution):
    neighborhood_of_solution = []
    for n in range(len(solution)):
        if n > 0:
            break
        else:
            print("n",n)
        width = solution.loc[n]["width"]
        height = solution.loc[n]["height"]

        solution.loc[n]["width"] = height
        solution.loc[n]["height"] = width
        solution.loc[n]["vertical"] = 1
        
        blf = BLF(solution, SCOPE, RESOLUTION)
        blf.run()
        mem = copy.deepcopy(solution)
        neighborhood_of_solution.append([mem, blf.length])

        idx1 = solution.loc[n]
        for m in range(len(solution)):
            idx2 = solution.loc[m]
            if m == n:
                continue

            mem = copy.deepcopy(solution)
            mem.loc[m] = idx1
            mem.loc[n] = idx2
            blf = BLF(mem, SCOPE, RESOLUTION)
            blf.run()
            
            neighborhood_of_solution.append([mem, blf.length])
            if m > 0 :
                break
            else:
                print("m",m)
        
    indexOfLastItemInTheList = len(neighborhood_of_solution[0]) - 1
    neighborhood_of_solution.sort(key=lambda x: x[indexOfLastItemInTheList])
    return neighborhood_of_solution

def tabu_search(first_solution, value, iters, size):
    count = 1
    solution = first_solution
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
            while i < len(best_solution):

                if best_solution[i] != solution.loc[i]:
                    first_exchange_node = best_solution.loc[i]
                    second_exchange_node = solution.loc[i]
                    break
                i = i + 1

            if [first_exchange_node, second_exchange_node] not in tabu_list and [
                second_exchange_node,
                first_exchange_node,
            ] not in tabu_list:
                tabu_list.append([first_exchange_node, second_exchange_node])
                found = True
                solution = best_solution.loc[:-1]
                length = neighborhood[index_of_best_solution][1]
                if length < best_value:
                    best_value = length
                    best_solution_ever = solution
            else:
                index_of_best_solution = index_of_best_solution + 1
                best_solution = neighborhood[index_of_best_solution]

        if len(tabu_list) >= size:
            tabu_list.pop(0)

        count = count + 1

    return best_solution_ever, best_value

def main(args=None):
    first_solution, value = generate_first_solution(args.File)

    best_sol, best_value = tabu_search(
        first_solution,
        value,
        args.Iterations,
        args.Size,
    )

    print(f"Best solution: {best_sol}, with total length: {best_value}.")


if __name__ == "__main__":
    start = time.perf_counter()

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
    end = time.perf_counter()
    print("[time cost] " + str(end-start) + "s")