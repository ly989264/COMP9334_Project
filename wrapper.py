# python version: python3.7
import os
from random_mode import *
from trace_mode import *

# if need to test all cases
def testing_all_cases():
    # read the file num_tests.txt to determine the number of tests
    if not os.path.exists("num_tests.txt"):
        print("The file num_tests.txt does not exist.")
    with open("num_tests.txt", "r") as f:
        num_of_test = int(f.read())

    # for each index from 1 to num_of_test
    for each_index in range(1,num_of_test+1):
        # get the mode from the mode_num.txt file
        with open("mode_"+str(each_index)+".txt", "r") as f:
            mode = f.read()
        print(f"Start running simulation No.{each_index}. Mode: {mode}.")
        if mode == "random":
            random_mode_launcher(each_index)  # launch the random mode simulation
            # the configuration read, simulation and result output are all included in this function
        else:
            trace_mode_launcher(each_index)  # launch the trace mode simulation
            # the configuration read, simulation and result output are all included in this function

# if need to test for certain case:
def testing_for_certain_case(simulation_num):
    # get the mode from the mode_num.txt file
    with open("mode_" + str(simulation_num) + ".txt", "r") as f:
        mode = f.read()
    print(f"Start running simulation No.{simulation_num}. Mode: {mode}.")
    if mode == "random":
        random_mode_launcher(simulation_num)  # launch the random mode simulation
        # the configuration read, simulation and result output are all included in this function
    else:
        trace_mode_launcher(simulation_num)  # launch the trace mode simulation
        # the configuration read, simulation and result output are all included in this func

# run
testing_all_cases()  # by default, testing all cases
# testing_for_certain_case(5)  # testing certain case