import os
import matplotlib.pyplot
import math

def mean_range(arr, start_index, end_index):
    sum = 0
    for i in range(start_index, end_index+1):
        sum+=arr[i]
    return sum/(end_index-start_index+1)

response_time_traces = []
for i in range(1,6):
    filename = "trace"+str(i)
    temp = []
    with open(filename, "r") as f:
        for each_line in f:
            temp.append(float(each_line))
    response_time_traces.append(temp)

# with open("traceresult", "w") as f:
#     for each in response_time_traces:
#         print(each, file=f)

mean_response_time = []
m = len(response_time_traces[0])
num = len(response_time_traces)
for each_index in range(m):
    sum = 0
    for each_arr_index in range(num):
        sum += response_time_traces[each_arr_index][each_index]
    mean_response_time.append(sum/num)

print(m)
print(len(mean_response_time))

w = 5000
mt_smooth = [0 for i in range(m-w)]
for i in range(0, m-w):
    if i <= w:
        mt_smooth[i] = mean_range(mean_response_time, 1, 2 * i -1)
    else:
        mt_smooth[i] = mean_range(mean_response_time, i-w, i+w)

matplotlib.pyplot.plot(mt_smooth)
matplotlib.pyplot.show()
