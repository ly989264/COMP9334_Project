from random_mode import *

def random_simulation(each_simulation_num, time_out, testing_min, testing_max, testing_step):
    #configuration
    lambda_value = 9.72
    alpha1 = 0.01
    alpha2 = 0.4
    beta_value = 0.86
    v1_value = 1.2
    v2_value = 1.47
    fogTimeToCloudTime = 0.6
    # start simulation
    current_simulation_num = 0
    each_fogTimeLimit = testing_min
    while each_fogTimeLimit <= testing_max:
        print("Current:", each_fogTimeLimit)
        for i in range(0, each_simulation_num):
            random_mode_simulation(lambda_value, alpha1, alpha2, beta_value, v1_value, v2_value, each_fogTimeLimit, fogTimeToCloudTime, time_out, current_simulation_num)
            current_simulation_num += 1
        each_fogTimeLimit += testing_step

#configuration
lambda_value = 9.72
alpha1 = 0.01
alpha2 = 0.4
beta_value = 0.86
v1_value = 1.2
v2_value = 1.47
fogTimeToCloudTime = 0.6
# start simulation
current_fogTimeLimit = 0.088
time_out = 1000
current_simulation_num = 10
random_mode_simulation(lambda_value, alpha1, alpha2, beta_value, v1_value, v2_value, current_fogTimeLimit, fogTimeToCloudTime, time_out, current_simulation_num)




# todo: find a way to avoid the fluctuation at the first beginning