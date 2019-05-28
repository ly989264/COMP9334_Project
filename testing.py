# this program implements the random mode
import random
import math
import matplotlib.pyplot
from queue import Queue


def generate_arrival(lambda_value):
    return -1 * math.log(1 - random.uniform(0, 1)) / lambda_value

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

def generate_network_latenty(v1_value, v2_value):
    return random.uniform(v1_value, v2_value)

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
    return (job_id, fog_processing_time, network_processing_time, cloud_processing_time, arrive_time)

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

def random_mode_simulation(lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, fogTimeLimit, fogTimeToCloudTime, time_end, simulation_num):
    random.seed(1)  # todo: may also consider to save and get seed to and from file
    # output file
    mrt_filename = "mrt_"+str(simulation_num)+".txt"
    fogdep_filename = "fog_dep_"+str(simulation_num)+".txt"
    netdep_filename = "net_dep_"+str(simulation_num)+".txt"
    clouddep_filename = "cloud_dep_"+str(simulation_num)+".txt"
    mrt_stream = open(mrt_filename, "w")
    fogdep_stream = open(fogdep_filename, "w")
    netdep_stream = open(netdep_filename, "w")
    clouddep_stream = open(clouddep_filename, "w")
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
    # start simulation
    # initialization
    job_arr = []
    job_arr.append(generate_job_tuple(0, lambda_value, alpha1_value, alpha2_value, beta_value, v1_value, v2_value, 0, fogTimeLimit, fogTimeToCloudTime))
    if job_arr[0][4]>time_end:
        print("The first job's arrive time is bigger than the time end, ending...")
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
            print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
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
            print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
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
            print(f"{job_arr[network_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=netdep_stream)
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
            print(f"{job_arr[cloud_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=clouddep_stream)
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
            print("This condition should not happen.")
            return
        master_clock = current_new_time

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

def track_mode_launcher(simulation_num):  # assume that the format of the file content is correct
    with open("para_"+str(simulation_num)+".txt", "r") as f:
        fogTimeLimit = float(f.readline())
        fogTimeToCloudTime = float(f.readline())
    arrive_arr = []
    service_arr = []
    network_arr = []
    with open("arrival_"+str(simulation_num)+".txt", "r") as f:
        for each_line in f:
            arrive_arr.append(float(each_line))
    with open("service_"+str(simulation_num)+".txt", "r") as f:
        for each_line in f:
            service_arr.append(float(each_line))
    with open("network_"+str(simulation_num)+".txt", "r") as f:
        for each_line in f:
            network_arr.append(float(each_line))
    fogservice_arr=[]
    cloudservice_arr=[]
    for each_element in service_arr:
        if each_element <= fogTimeLimit:
            fogservice_arr.append(each_element)
            cloudservice_arr.append(0)
        else:
            fogservice_arr.append(fogTimeLimit)
            cloudservice_arr.append(fogTimeToCloudTime*(each_element-fogTimeLimit))
    # output file
    mrt_filename = "mrt_" + str(simulation_num) + ".txt"
    fogdep_filename = "fog_dep_" + str(simulation_num) + ".txt"
    netdep_filename = "net_dep_" + str(simulation_num) + ".txt"
    clouddep_filename = "cloud_dep_" + str(simulation_num) + ".txt"
    mrt_stream = open(mrt_filename, "w")
    fogdep_stream = open(fogdep_filename, "w")
    netdep_stream = open(netdep_filename, "w")
    clouddep_stream = open(clouddep_filename, "w")
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
    # start simulation
    # initialization
    job_arr = []
    current_number = 0
    job_arr.append([0, fogservice_arr[current_number], network_arr[current_number], cloudservice_arr[current_number], arrive_arr[current_number]])
    current_number += 1
    master_clock = 0
    time_array[0] = job_arr[0][-1]  # todo: should convince that this is necessary
    end_flag = False  # when all elements in time array is None, convert the end flag to True
    print(arrive_arr)
    print(fogservice_arr)
    print(network_arr)
    print(cloudservice_arr)
    print("Start simulation.")
    print("time array: ", end='')
    print(time_array)
    print("**************************************")
    while not end_flag:  # event driven
        next_time_tuple = compare_event_time(time_array[0], time_array[1], time_array[2], time_array[3], time_array[4])
        current_new_time = next_time_tuple[1]
        if next_time_tuple[0] == 0:  # new arrival
            # print("Event: 0.")
            # first, update the remain-processing-time in the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(fog_container)
            # also need to modify the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(cloud_container)
            # then, insert the new job in the fog container
            fog_container.append([job_arr[-1][0], job_arr[-1][1]])
            # then, sort the fog container
            fog_container.sort(key=lambda x: x[1])
            # then, generate a new job in the job arr
            current_job_num_in_arr = len(job_arr)
            if current_number >= len(arrive_arr):
                # no need to append because there is no job left
                time_array[0]=None
            else:
                job_arr.append([current_number, fogservice_arr[current_number], network_arr[current_number], cloudservice_arr[current_number], arrive_arr[current_number]])
                time_array[0] = job_arr[-1][-1]
            # finally, update the time_array information
            if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                time_array[2] = None
            else:
                time_array[1] = None
                time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time-master_clock)
            current_number += 1
            # the other two time properties cannot get updated in this condition
        elif next_time_tuple[0] == 1:  # job departure through next_fog_departure_permanent_time
            # print("Event: 1.")
            # the job leaves must be the first one of the fog container
            # first, append the information, arrival time \r departure time, each with four-digit precesion
            print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
            # then, delete the first pair in fog container
            current_length = len(fog_container)
            fog_container.pop(0)
            # finally, update the remain-processing-time in fog container and the time_array information
            if not fog_container:  # the fog container is empty, means that there is no job processing in the fog
                time_array[1] = None
                time_array[2] = None
            else:
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / current_length
                # only need to update time_array[1] and time_array[2]
                if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                    time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                    time_array[2] = None
                else:
                    time_array[1] = None
                    time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            # also need to modify the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(cloud_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)
        elif next_time_tuple[0] == 2:  # job departure through next_fog_departure_network_time
            # print("Event: 2.")
            # first, append the information, arrival time \r departure time to fogdep_stream
            print(f"{job_arr[fog_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=fogdep_stream)
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
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / current_length
            # also need to modify the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(cloud_container)
            # finally, update the time-array information
            if not fog_container:
                time_array[1] = None
                time_array[2] = None
            else:
                if job_arr[fog_container[0][0]][2] == 0:  # the first job to be finished in the fog container will leave permanently
                    time_array[1] = current_new_time + fog_container[0][1] * len(fog_container)
                    time_array[2] = None
                else:
                    time_array[1] = None
                    time_array[2] = current_new_time + fog_container[0][1] * len(fog_container)
            time_array[3]=current_new_time + network_container[0][1]
            # the time_array[0], and time_array[4] do not need to update
        elif next_time_tuple[0] == 3:  # job departure through next_network_departure_time
            # print("Event: 3.")
            # first, append the information to netdep_stream
            print(f"{job_arr[network_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=netdep_stream)
            # then, update the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(cloud_container)
            # also need to modify the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(fog_container)
            # then, append this job in the cloud container
            cloud_container.append([network_container[0][0], job_arr[network_container[0][0]][3]])
            # then, sort the cloud container
            cloud_container.sort(key=lambda x: x[1])
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)  # todo: ???
            # then, delete this job in the network container
            network_container.pop(0)
            # finally, update the time array information
            # only need to update the time_array[3] and time_array[4]
            if not network_container:  # network container is empty
                time_array[3] = None
            else:  # network container is not empty
                time_array[3] = current_new_time + network_container[0][1]
            # in this condition, cloud container should not be empty
            time_array[4] = current_new_time + cloud_container[0][1] * len(cloud_container)
        elif next_time_tuple[0] == 4:  # job departure through next_cloud_departure_time
            # print("Event: 4.")
            # first, append the information to clouddep_stream
            print(f"{job_arr[cloud_container[0][0]][4]:.4f}\t{current_new_time:.4f}", file=clouddep_stream)
            # then, remove the finished job in the cloud container
            current_length = len(cloud_container)
            cloud_container.pop(0)
            # then, update the remain-processing-time in the cloud container
            if not cloud_container:  # cloud container is empty
                pass  # do nothing
            else:  # cloud container is not empty
                for each_pair in cloud_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / current_length
            # also need to modify the fog container
            if not fog_container:  # fog container is empty
                pass  # do nothing
            else:  # fog container is not empty
                for each_pair in fog_container:  # update the remain-processing-time
                    each_pair[1] = each_pair[1] - (current_new_time - master_clock) / len(fog_container)
            # finally, update the time array information
            # only need to update time_array[4]
            if not cloud_container:  # cloud container is empty
                time_array[4] = None
            else:  # cloud container is not empty
                time_array[4] = current_new_time + cloud_container[0][1] * len(cloud_container)
            # also, update the network
            if network_container:
                for each_pair in network_container:
                    each_pair[1] -= (current_new_time - master_clock)
        else:
            # end of the simulation
            print("Time to end.")
            end_flag = True
        print("master clock: ", end='')
        print(current_new_time)
        print("time array: ",end ='')
        print(time_array)
        print("job arr: ", end='')
        print(job_arr)
        print("fog container: ", end='')
        print(fog_container)
        print("network container: ", end='')
        print(network_container)
        print("cloud container: ", end='')
        print(cloud_container)
        print("*******************************")
        master_clock = current_new_time  # todo

# testing
track_mode_launcher(3)