# this program is used to check the correctness of the random mode
import random
import math
import os
import matplotlib.pyplot
from queue import Queue


# function used to generate random arrival time in random mode
def generate_arrival(lambda_value):
    return -1 * math.log(1 - random.uniform(0, 1)) / lambda_value


# function used to generate random overall fog operation time in random mode
def generate_fog_time(alpha1_value, alpha2_value, beta_value):
    # return math.log((1-beta_value)*random.uniform(0,1)/r+alpha1_value**(1-beta_value))/(1-beta_value)
    random_num = random.uniform(0,1)
    if random_num == 0:
        result = alpha1_value
    elif random_num == 1:
        result = alpha2_value
    else:
        result = (random_num*(alpha2_value**(1-beta_value)-alpha1_value**(1-beta_value))+alpha1_value**(1-beta_value))**(1/(1-beta_value))
    return result


# function used to generate random network delay time in random mode
def generate_network_latenty(v1_value, v2_value):
    return random.uniform(v1_value, v2_value)


# function used to generate random job tuple with certain format in random mode
def generate_job_tuple(job_id, lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, current_mc, fogTimeLimit, fogTimeToCloudTime):
    arrive_time = current_mc + generate_arrival(lambda_value)
    # note: The judgment of whether the new generated arrive time is bigger than the time_end is in the simulation
    overall_processing_time = generate_fog_time(alpha1_value, alpha2_value, beta_value)
    if overall_processing_time <= fogTimeLimit:
        fog_processing_time = overall_processing_time
        network_processing_time = 0
        cloud_processing_time = 0
    else:
        fog_processing_time = fogTimeLimit
        network_processing_time = generate_network_latenty(v1_value, v2_value)
        cloud_processing_time = (overall_processing_time - fogTimeLimit)*fogTimeToCloudTime
    f1 = open("arrival_5.txt", "a")
    f2 = open("service_5.txt", "a")
    f3 = open("network_5.txt", "a")
    f4 = open("para_5.txt", "w")
    print(arrive_time, file = f1)
    print(overall_processing_time, file = f2)
    if overall_processing_time <= fogTimeLimit:
        print("0", file = f3)
    else:
        print(network_processing_time, file=f3)
    print(f"{fogTimeLimit}\n{fogTimeToCloudTime}", file = f4)
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    return job_id, fog_processing_time, network_processing_time, cloud_processing_time, arrive_time


# function used to compare the event time tuple, and find the smallest one, used in all modes
def compare_event_time(next_arrive, next_fog_departure_permanent, next_fog_departure_network, next_network_departure, next_cloud_departure):
    curr_arr = []
    if not next_arrive is None:
        curr_arr.append((0,next_arrive))
    if not next_fog_departure_permanent is None:
        curr_arr.append((1,next_fog_departure_permanent))
    if not next_fog_departure_network is None:
        curr_arr.append((2,next_fog_departure_network))
    if not next_network_departure is None:
        curr_arr.append((3,next_network_departure))
    if not next_cloud_departure is None:
        curr_arr.append((4,next_cloud_departure))
    if not curr_arr:  # all None
        return (5, None)  # indicate that it is done
    curr_arr.sort(key = lambda x : x[1])
    tup = curr_arr[0]
    return tup

# function to simulate in random mode
# used for seaking the best value of fogTimeLimit
# do not write to mrt, fog_dep, network_dep and cloud_dep files
# save seed file with "rt" prefix
# also, save the trace file in the trace folder
# with the name format "./trace/trace_fogTimeLimit_time_end_simulationNum.txt
def random_mode_simulation_generate_trace(lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, fogTimeLimit, fogTimeToCloudTime, time_end, simulation_num):
    if not os.path.exists("./trace"):
        os.mkdir("trace")
    trace_filename = "./trace/trace_"+f"{fogTimeLimit:.4f}"+"_"+str(time_end)+"_"+str(simulation_num)+".txt"
    # need to write to the trace file
    # save seed to file and restore seed from file
    if not os.path.exists("./seed"):
        os.mkdir("seed")
    seed_filename = "./seed/rt_seed_"+str(simulation_num)+".txt"
    if not os.path.exists(seed_filename):
        seed = simulation_num
        random.seed(seed)
        with open(seed_filename, "w") as f:
            print(seed, file=f)
    else:
        with open(seed_filename, "r") as f:
            seed = int(f.read())
        random.seed(seed)
    # variables to maintain
    master_clock = 0
    event_type = None
    current_job_id = None
    time_array = [None, None, None, None, None]
    # /***********next_arrive_time ****************************************/
    # /*****************next_fog_departure_permanent_time *****************/
    # /***********************next_fog_departure_network_time *************/
    # /*****************************next_network_departure_time ***********/
    # /***********************************next_cloud_departure_time *******/
    # containers
    fog_container = []  # list, ordered by the fog processing time
    network_container = []  # queue
    cloud_container = []  # list, ordered by the cloud processing time
    response_time_container = []#todo new added
    # start simulation
    # initialization
    job_arr = []
    job_arr.append(generate_job_tuple(0, lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, 0, fogTimeLimit, fogTimeToCloudTime))
    if job_arr[0][4]>time_end:
        print("The first job's arrive time is bigger than the time end, ending...")  # for debug use only
        return
    master_clock = 0
    time_array[0]=job_arr[0][-1]  # todo: should convince that this is necessary
    while master_clock <= time_end:  # event driven
        next_time_tuple = compare_event_time(time_array[0], time_array[1], time_array[2], time_array[3], time_array[4])
        current_new_time = next_time_tuple[1]
        if next_time_tuple[0] == 0:  # new arrival
            # first, update the remain-processing-time in the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/len(fog_container)
            # also need to modify the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:
                    each_pair[1]=each_pair[1]-(current_new_time-master_clock)/len(cloud_container)
            # then, insert the new job in the fog container
            fog_container.append([job_arr[-1][0], job_arr[-1][1]])
            # then, sort the fog container
            fog_container.sort(key = lambda x : x[1])
            # then, generate a new job in the job arr
            current_job_num_in_arr = len(job_arr)
            job_arr.append(generate_job_tuple(current_job_num_in_arr, lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, current_new_time, fogTimeLimit, fogTimeToCloudTime))
            # finally, update the time_array information
            time_array[0]=job_arr[-1][-1]
            if job_arr[fog_container[0][0]][2]==0:  # the first job to be finished in the fog container will leave permanently
                time_array[1]=current_new_time+fog_container[0][1]*len(fog_container)
                time_array[2]=None
            else:
                time_array[1]=None
                time_array[2]=current_new_time+fog_container[0][1]*len(fog_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
            # the other two time properties cannot get updated in this condition
        elif next_time_tuple[0] == 1:  # job departure through next_fog_departure_permant_time
            # the job leaves must be the first one of the fog container
            # first, append the information, arrival time \r departure time, each with four-digit precesion
            # print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
            # update the overall_time and overall_num
            response_time_container.append(current_new_time - job_arr[fog_container[0][0]][4])  # todo: new added
            # then, delete the first pair in fog container
            current_length = len(fog_container)
            fog_container.pop(0)
            # finally, update the remain-processing-time in fog container and the time_array information
            if not fog_container:  # the fog container is empty, means that there is no job processing in the fog
                time_array[1]=None
                time_array[2]=None
            else:
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/current_length
                # only need to update time_array[1] and time_array[2]
                if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                    time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                    time_array[2] = None
                else:
                    time_array[1] = None
                    time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            # also need to modify the cloud container
            if not cloud_container:
                pass
            else:
                for each_pair in cloud_container:
                    each_pair[1]=each_pair[1]-(current_new_time-master_clock)/len(cloud_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)
        elif next_time_tuple[0] == 2:  # job departure through next_fog_departure_network_time
            # first, append the information, arrival time \r departure time to fogdep_stream
            # print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)
            # then, append the job information finished to the network container
            network_container.append([fog_container[0][0], job_arr[fog_container[0][0]][2]])
            network_container.sort(key = lambda x: x[1])
            # then, delete the first pair in the fog container
            current_length = len(fog_container)
            fog_container.pop(0)
            # then, update the remain-processing-time in the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/current_length
            # also need to modify the cloud container
            if not cloud_container:
                pass
            else:
                for each_pair in cloud_container:
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock)/len(cloud_container)
            # finally, update the time-array information
            if not fog_container:
                time_array[1]=None
                time_array[2]=None
            else:
                if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                    time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                    time_array[2] = None
                else:
                    time_array[1] = None
                    time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            time_array[3] =current_new_time + network_container[0][1]
            # the time_array[0], and time_array[4] do not need to update
        elif next_time_tuple[0] == 3:  # job departure through next_network_departure_time
            # first, append the information to netdep_stream
            # print(f"{job_arr[network_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=netdep_stream)
            # then, update the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/len(cloud_container)
            # also need to modify the fog container
            if not fog_container:
                pass
            else:
                for each_pair in fog_container:
                    each_pair[1] = each_pair[1] - (current_new_time-master_clock)/len(fog_container)
            # then, append this job in the cloud container
            cloud_container.append([network_container[0][0], job_arr[network_container[0][0]][3]])
            # then, sort the cloud container
            cloud_container.sort(key=lambda x: x[1])
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
            # then, delete this job in the network container
            network_container.pop(0)
            # finally, update the time array information
            # only need to update the time_array[3] and time_array[4]
            if not network_container:  # network container is empty
                time_array[3]=None
            else:  # network container is not empty
                time_array[3] = current_new_time + network_container[0][1]
            # in this condition, cloud container should not be empty
            time_array[4] = current_new_time + cloud_container[0][1] * len(cloud_container)
        elif next_time_tuple[0] == 4:  # job departure through next_cloud_departure_time
            # first, append the information to clouddep_stream
            # print(f"{job_arr[cloud_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=clouddep_stream)
            # update the overall_time and overall_num
            response_time_container.append(current_new_time - job_arr[cloud_container[0][0]][4])  # todo: new added
            # then, remove the finished job in the cloud container
            current_length = len(cloud_container)
            cloud_container.pop(0)
            # then, update the remain-processing-time in the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/current_length
            # also need to modify the fog container
            if not fog_container:
                pass
            else:
                for each_pair in fog_container:
                    each_pair[1] = each_pair[1] - (current_new_time-master_clock)/len(fog_container)
            # finally, update the time array information
            # only need to update time_array[4]
            if not cloud_container:  # cloud container is empty
                time_array[4]=None
            else:  # cloud container is not empty
                time_array[4] = current_new_time + cloud_container[0][1] * len(cloud_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
        else:
            # this condition should not happen
            print("This condition should not happen.")  # for debug use only
            return
        master_clock = current_new_time
    with open(trace_filename, "w") as f:
        for each_trace in response_time_container:
            print(each_trace, file = f)


# function to simulate in random mode
def random_mode_simulation(lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, fogTimeLimit, fogTimeToCloudTime, time_end, simulation_num):
    # save seed to file and restore seed from file
    if not os.path.exists("./seed"):
        os.mkdir("seed")
    seed_filename = "./seed/seed_"+str(simulation_num)+".txt"
    if not os.path.exists(seed_filename):
        seed = simulation_num
        random.seed(seed)
        with open(seed_filename, "w") as f:
            print(seed, file=f)
    else:
        with open(seed_filename, "r") as f:
            seed = int(f.read())
        random.seed(seed)
    # output file
    mrt_filename = "mrt_"+str(simulation_num)+".txt"
    fogdep_filename = "fog_dep_"+str(simulation_num)+".txt"
    netdep_filename = "net_dep_"+str(simulation_num)+".txt"
    clouddep_filename = "cloud_dep_"+str(simulation_num)+".txt"
    mrt_stream = open(mrt_filename, "w")
    fogdep_stream = open(fogdep_filename, "w")
    netdep_stream = open(netdep_filename, "w")
    clouddep_stream = open(clouddep_filename, "w")
    fogdep_arr = []# improve
    netdep_arr = []# improve
    clouddep_arr = []# improve
    # variables to maintain
    master_clock = 0
    event_type = None
    current_job_id = None
    overall_time = 0  # todo
    overall_num = 0  # todo
    time_array = [None, None, None, None, None]
    # /***********next_arrive_time ****************************************/
    # /*****************next_fog_departure_permanent_time *****************/
    # /***********************next_fog_departure_network_time *************/
    # /*****************************next_network_departure_time ***********/
    # /***********************************next_cloud_departure_time *******/
    # containers
    fog_container = []  # list, ordered by the fog processing time
    network_container = []  # queue
    cloud_container = []  # list, ordered by the cloud processing time
    # start simulation
    # initialization
    job_arr = []
    job_arr.append(generate_job_tuple(0, lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, 0, fogTimeLimit, fogTimeToCloudTime))
    if job_arr[0][4]>time_end:
        print("The first job's arrive time is bigger than the time end, ending...")  # for debug use only
        return
    master_clock = 0
    time_array[0]=job_arr[0][-1]  # todo: should convince that this is necessary
    while master_clock <= time_end:  # event driven
        next_time_tuple = compare_event_time(time_array[0], time_array[1], time_array[2], time_array[3], time_array[4])
        current_new_time = next_time_tuple[1]
        if next_time_tuple[0] == 0:  # new arrival
            # first, update the remain-processing-time in the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/len(fog_container)
            # also need to modify the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:
                    each_pair[1]=each_pair[1]-(current_new_time-master_clock)/len(cloud_container)
            # then, insert the new job in the fog container
            fog_container.append([job_arr[-1][0], job_arr[-1][1]])
            # then, sort the fog container
            fog_container.sort(key = lambda x : x[1])
            # then, generate a new job in the job arr
            current_job_num_in_arr = len(job_arr)
            job_arr.append(generate_job_tuple(current_job_num_in_arr, lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, current_new_time, fogTimeLimit, fogTimeToCloudTime))
            # finally, update the time_array information
            time_array[0]=job_arr[-1][-1]
            if job_arr[fog_container[0][0]][2]==0:  # the first job to be finished in the fog container will leave permanently
                time_array[1]=current_new_time+fog_container[0][1]*len(fog_container)
                time_array[2]=None
            else:
                time_array[1]=None
                time_array[2]=current_new_time+fog_container[0][1]*len(fog_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
            # the other two time properties cannot get updated in this condition
        elif next_time_tuple[0] == 1:  # job departure through next_fog_departure_permant_time
            # the job leaves must be the first one of the fog container
            # first, append the information, arrival time \r departure time, each with four-digit precesion
            # print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
            fogdep_arr.append([job_arr[fog_container[0][0]][4], current_new_time])
            # update the overall_time and overall_num
            overall_num += 1  # todo
            overall_time += (current_new_time - job_arr[fog_container[0][0]][4])  # todo
            # then, delete the first pair in fog container
            current_length = len(fog_container)
            fog_container.pop(0)
            # finally, update the remain-processing-time in fog container and the time_array information
            if not fog_container:  # the fog container is empty, means that there is no job processing in the fog
                time_array[1]=None
                time_array[2]=None
            else:
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/current_length
                # only need to update time_array[1] and time_array[2]
                if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                    time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                    time_array[2] = None
                else:
                    time_array[1] = None
                    time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            # also need to modify the cloud container
            if not cloud_container:
                pass
            else:
                for each_pair in cloud_container:
                    each_pair[1]=each_pair[1]-(current_new_time-master_clock)/len(cloud_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)
        elif next_time_tuple[0] == 2:  # job departure through next_fog_departure_network_time
            # first, append the information, arrival time \r departure time to fogdep_stream
            # print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
            fogdep_arr.append([job_arr[fog_container[0][0]][4], current_new_time])
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)
            # then, append the job information finished to the network container
            network_container.append([fog_container[0][0], job_arr[fog_container[0][0]][2]])
            network_container.sort(key = lambda x: x[1])
            # then, delete the first pair in the fog container
            current_length = len(fog_container)
            fog_container.pop(0)
            # then, update the remain-processing-time in the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/current_length
            # also need to modify the cloud container
            if not cloud_container:
                pass
            else:
                for each_pair in cloud_container:
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock)/len(cloud_container)
            # finally, update the time-array information
            if not fog_container:
                time_array[1]=None
                time_array[2]=None
            else:
                if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                    time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                    time_array[2] = None
                else:
                    time_array[1] = None
                    time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            time_array[3] =current_new_time + network_container[0][1]
            # the time_array[0], and time_array[4] do not need to update
        elif next_time_tuple[0] == 3:  # job departure through next_network_departure_time
            # first, append the information to netdep_stream
            # print(f"{job_arr[network_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=netdep_stream)
            netdep_arr.append([job_arr[network_container[0][0]][4], current_new_time])
            # then, update the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/len(cloud_container)
            # also need to modify the fog container
            if not fog_container:
                pass
            else:
                for each_pair in fog_container:
                    each_pair[1] = each_pair[1] - (current_new_time-master_clock)/len(fog_container)
            # then, append this job in the cloud container
            cloud_container.append([network_container[0][0], job_arr[network_container[0][0]][3]])
            # then, sort the cloud container
            cloud_container.sort(key=lambda x: x[1])
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
            # then, delete this job in the network container
            network_container.pop(0)
            # finally, update the time array information
            # only need to update the time_array[3] and time_array[4]
            if not network_container:  # network container is empty
                time_array[3]=None
            else:  # network container is not empty
                time_array[3] = current_new_time + network_container[0][1]
            # in this condition, cloud container should not be empty
            time_array[4] = current_new_time + cloud_container[0][1] * len(cloud_container)
        elif next_time_tuple[0] == 4:  # job departure through next_cloud_departure_time
            # first, append the information to clouddep_stream
            # print(f"{job_arr[cloud_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=clouddep_stream)
            clouddep_arr.append([job_arr[cloud_container[0][0]][4], current_new_time])
            # update the overall_time and overall_num
            overall_num += 1  # todo
            overall_time += (current_new_time - job_arr[cloud_container[0][0]][4])  # todo
            # then, remove the finished job in the cloud container
            current_length = len(cloud_container)
            cloud_container.pop(0)
            # then, update the remain-processing-time in the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1]-(current_new_time-master_clock)/current_length
            # also need to modify the fog container
            if not fog_container:
                pass
            else:
                for each_pair in fog_container:
                    each_pair[1] = each_pair[1] - (current_new_time-master_clock)/len(fog_container)
            # finally, update the time array information
            # only need to update time_array[4]
            if not cloud_container:  # cloud container is empty
                time_array[4]=None
            else:  # cloud container is not empty
                time_array[4] = current_new_time + cloud_container[0][1] * len(cloud_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
        else:
            # this condition should not happen
            print("This condition should not happen.")  # for debug use only
            return
        master_clock = current_new_time
    print(f"{overall_time/overall_num:.4f}", file=mrt_stream)  # todo
    fogdep_arr.sort(key = lambda x: x[0])
    netdep_arr.sort(key = lambda x: x[0])
    clouddep_arr.sort(key = lambda x: x[0])
    for each_pair in fogdep_arr:
        print(f"{each_pair[0]:.4f}\t{each_pair[1]:.4f}", file=fogdep_stream)
    for each_pair in netdep_arr:
        print(f"{each_pair[0]:.4f}\t{each_pair[1]:.4f}", file=netdep_stream)
    for each_pair in clouddep_arr:
        print(f"{each_pair[0]:.4f}\t{each_pair[1]:.4f}", file=clouddep_stream)
    fogdep_stream.close()
    netdep_stream.close()
    clouddep_stream.close()


# function that read certain parameters and launch the random mode simulation
def random_mode_launcher(simulation_num):  # assume that the format of the file content is correct
    with open("para_" + str(simulation_num) + ".txt", "r") as f:
        fogTimeLimit = float(f.readline())
        fogTimeToCloudTime = float(f.readline())
        time_end = float(f.readline())
    with open("arrival_"+str(simulation_num)+".txt", "r") as f:
        lambda_value = float(f.readline())
    with open("service_"+str(simulation_num)+".txt", "r") as f:
        alpha1_value = float(f.readline())
        alpha2_value = float(f.readline())
        beta_value = float(f.readline())
    with open("network_"+str(simulation_num)+".txt", "r") as f:
        v1_value = float(f.readline())
        v2_value = float(f.readline())
    # call the simulation function for random mode
    random_mode_simulation(lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, fogTimeLimit, fogTimeToCloudTime, time_end, simulation_num)





# todo: testing the random mode
# check the correctness of the seed saving and restoring
# submit at least three sets of sample output files?
from trace_mode import *
trace_mode_launcher(5)
