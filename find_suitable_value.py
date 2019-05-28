import os
import math
import statistics
import matplotlib.pyplot
import numpy as np
from random_mode import *


# this function is used to calculate the mean value of a certain range
def mean_range(arr, start_index, end_index):
    sum = 0
    for i in range(start_index, end_index+1):
        sum+=arr[i]
    return sum/(end_index-start_index+1)


# this function is used to generate the trace file
def generate_trace_file(fogTimeLimit, time_end, simulation_num):
    # configuration
    lambda_value = 9.72
    alpha1 = 0.01
    alpha2 = 0.4
    beta_value = 0.86
    v1_value = 1.2
    v2_value = 1.47
    fogTimeToCloudTime = 0.6
    # start generating the trace files
    for current_simulation_num in range(0, simulation_num):
        random_mode_simulation_generate_trace(lambda_value, alpha1, alpha2, beta_value, v1_value, v2_value, fogTimeLimit, fogTimeToCloudTime, time_end, current_simulation_num)


# this function is used to remove the transient and draw the plot
def transient_remove_precedure(fogTimeLimit, time_end, w):
    smallest_line_num = None
    num = 0
    response_time_traces = []
    str_pattern = "trace_"+f"{fogTimeLimit:.4f}"+"_"+str(time_end)
    for each_filename in os.listdir("./trace"):
        if each_filename.startswith(str_pattern):
            temp = []
            final_filename = "./trace/"+each_filename
            with open(final_filename, "r") as f:
                for each_line in f:
                    temp.append(float(each_line))
            response_time_traces.append(temp)
            if not smallest_line_num:
                smallest_line_num = len(temp)
            else:
                if smallest_line_num > len(temp):
                    smallest_line_num = len(temp)
            num += 1
    mean_response_time = []
    m = smallest_line_num
    for each_index in range(m):
        sum = 0
        for each_arr_index in range(num):
            sum += response_time_traces[each_arr_index][each_index]
        mean_response_time.append(sum/num)
    mt_smooth = [0 for i in range(m-w)]
    for i in range(0, m-w):
        if i <= w:
            mt_smooth[i] = mean_range(mean_response_time, 1, 2*i-1)
        else:
            mt_smooth[i] = mean_range(mean_response_time, i-w, i+w)
    if not os.path.exists("./figure"):
        os.mkdir("figure")
    matplotlib.pyplot.plot(mt_smooth)
    matplotlib.pyplot.title("fogTimeLimit: "+f"{fogTimeLimit:.4f}" +
                            " timeEnd: "+str(time_end)+" w: "+str(w))
    figure_name = "./figure/"+str(fogTimeLimit)+"_"+str(time_end)+"_"+str(w)+".png"
    # matplotlib.pyplot.show()
    matplotlib.pyplot.savefig(figure_name)
    matplotlib.pyplot.clf()


# this function is used to calculate the confidence interval with 95% probability
def calculate_confidence_interval_095(fogTimeLimit, time_end, l_value):
    # first, get the mean response time of all replications
    if not os.path.exists("./trace"):
        print("Trace folder does not exist.")
        return
    str_pattern = "trace_"+f"{fogTimeLimit:.4f}"+"_"+str(time_end)
    mean_response_arr = []
    for each_filename in os.listdir("./trace"):
        if each_filename.startswith(str_pattern):
            filename = "./trace/"+each_filename
            sum = 0
            cnt = 0
            with open(filename, "r") as f:
                for each_line in f:
                    if cnt > l_value:
                        sum += float(each_line)
                    cnt += 1
            mean_response_arr.append(sum/(cnt-l_value))
    # then, calculate the sample mean and sample standard deviation
    sample_mean = statistics.mean(mean_response_arr)
    sample_deviation = statistics.stdev(mean_response_arr)
    # need to know the value of tn-1,1-alpha/2
    # default number of files is 20, and 95%
    # t19,0.975
    t_value = 2.093
    lower_case = sample_mean - t_value * sample_deviation / (math.sqrt(20))
    upper_case = sample_mean + t_value * sample_deviation / (math.sqrt(20))
    return lower_case, upper_case, sample_mean


# this function is used to calculate the confidence interval with 90% probability
def calculate_confidence_interval_090(fogTimeLimit, time_end, l_value):
    # first, get the mean response time of all replications
    if not os.path.exists("./trace"):
        print("Trace folder does not exist.")
        return
    str_pattern = "trace_"+f"{fogTimeLimit:.4f}"+"_"+str(time_end)
    mean_response_arr = []
    for each_filename in os.listdir("./trace"):
        if each_filename.startswith(str_pattern):
            filename = "./trace/"+each_filename
            sum = 0
            cnt = 0
            with open(filename, "r") as f:
                for each_line in f:
                    if cnt > l_value:
                        sum += float(each_line)
                    cnt += 1
            mean_response_arr.append(sum/(cnt-l_value))
    # then, calculate the sample mean and sample standard deviation
    sample_mean = statistics.mean(mean_response_arr)
    sample_deviation = statistics.stdev(mean_response_arr)
    # need to know the value of tn-1,1-alpha/2
    # default number of files is 20, and 90%
    # t19,0.95
    t_value = 1.729
    lower_case = sample_mean - t_value * sample_deviation / (math.sqrt(20))
    upper_case = sample_mean + t_value * sample_deviation / (math.sqrt(20))
    return lower_case, upper_case, sample_mean


# this function is used to draw the approximate visual test
def draw_visual_test(filename):
    fogTimeLimit_arr = []
    lower_arr = []
    upper_arr = []
    mean_arr = []
    with open(filename) as f:
        for each_line in f:
            print(each_line)
            current_list = each_line.split(" ")
            fogTimeLimit_arr.append(float(current_list[0]))
            lower_arr.append(float(current_list[1]))
            upper_arr.append(float(current_list[2]))
            mean_arr.append(float(current_list[3]))
    length = len(fogTimeLimit_arr)

    for i in range(length):
        matplotlib.pyplot.plot([fogTimeLimit_arr[i], fogTimeLimit_arr[i]], [lower_arr[i], upper_arr[i]])
        matplotlib.pyplot.scatter(fogTimeLimit_arr[i], mean_arr[i])
        # matplotlib.pyplot.plot([fogTimeLimit_arr[0], fogTimeLimit_arr[-1]], [mean_arr[i], mean_arr[i]], linewidth = "0.3", c="#666666")
    matplotlib.pyplot.title("Approximate Visual Test")
    matplotlib.pyplot.xlabel("fogTimeLimit")
    matplotlib.pyplot.ylabel("Mean Response Time")
    matplotlib.pyplot.show()
    matplotlib.pyplot.clf()


# this function is used to compare two systems with difference fogTimeLimit values, with 90% probability
def t_test_090(fogTimeLimit1, fogTimeLimit2, time_end, l_value, simulation_num):
    str_pattern1 = "trace_" + f"{fogTimeLimit1:.4f}" + "_" + str(time_end)
    mean_response_arr1 = []
    for each_filename in os.listdir("./trace"):
        if each_filename.startswith(str_pattern1):
            filename = "./trace/" + each_filename
            sum = 0
            cnt = 0
            with open(filename, "r") as f:
                for each_line in f:
                    if cnt > l_value:
                        sum += float(each_line)
                    cnt += 1
            mean_response_arr1.append(sum / (cnt - l_value))
    str_pattern2 = "trace_" + f"{fogTimeLimit2:.4f}" + "_" + str(time_end)
    mean_response_arr2 = []
    for each_filename in os.listdir("./trace"):
        if each_filename.startswith(str_pattern2):
            filename = "./trace/" + each_filename
            sum = 0
            cnt = 0
            with open(filename, "r") as f:
                for each_line in f:
                    if cnt > l_value:
                        sum += float(each_line)
                    cnt += 1
            mean_response_arr2.append(sum / (cnt - l_value))
    difference_arr = []
    for i in range(0, simulation_num):
        difference_arr.append(mean_response_arr2[i]-mean_response_arr1[i])
    sample_mean = statistics.mean(difference_arr)
    sample_deviation = statistics.stdev(difference_arr)
    # need to know the value of tn-1,1-alpha/2
    # default number of files is 20, and 90%
    # t19,0.95
    t_value = 1.729
    lower_case = sample_mean - t_value * sample_deviation / (math.sqrt(20))
    upper_case = sample_mean + t_value * sample_deviation / (math.sqrt(20))
    with open("t_test_result.txt", "a") as f:
        print(f"{fogTimeLimit1:.4f} {fogTimeLimit2:.4f} {lower_case:.4f} {upper_case:.4f} {sample_mean:.4f}", file = f)


# the processing used to choose a suitable value is a little bit manual

# Part I
# do the simulation
# simu_num = 20
# time_end_arr = [1000, 3000, 10000]
# w_arr = [2000]
# fogTimeLimit_min = 0.09
# fogTimeLimit_max = 0.13
# fogTimeLimit_step = 0.001
# current_time = fogTimeLimit_min
# f=open("confidence_result.txt", "w")
# while current_time <= fogTimeLimit_max:
#     for current_time_end in time_end_arr:
#         for current_w in w_arr:
#             print(f"Currently working on {current_time}.")
#             # if choose the first two, used to simulate and remove transient
#             # generate_trace_file(current_time, current_time_end, simu_num)
#             # transient_remove_precedure(current_time, current_time_end, current_w)
#             # if choose the last one, used to calculate the confidence interval
#             result_tuple = calculate_confidence_interval_090(current_time, current_time_end, 5000)
#             print(f"{current_time:.4f} {result_tuple[0]:.4f} {result_tuple[1]:.4f} {result_tuple[2]:.4f}", file = f)
#     current_time += fogTimeLimit_step
# f.close()

# Part II
# draw the visual test
# prerequirement: all confidence interval results have been written to the confidence_result.txt file
# draw_visual_test("confidence_result.txt")

# Part III
# do the t-test
# start = 0.098
# # end = 0.120
# # i = start
# # while i <= end:
# #     j = i
# #     while j <= end:
# #         print(f"Currently working on ({i}, {j}).")
# #         t_test_090(i, j, 3000, 2000, 20)
# #         j += 0.001
# #     i += 0.001
# start = 0.107
# i = 0.098
# while i<= 0.12:
#     t_test_090(start, i, 3000, 2000, 20)
#     i+=0.001