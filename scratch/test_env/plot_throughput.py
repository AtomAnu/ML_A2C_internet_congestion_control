import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

a3c = pd.read_csv('network_obs.csv')
new = pd.read_csv('test_result_2.csv')

a3c_t = a3c[['Throughput']]
new_t = new[['Throughput']]

count = 0
a_throughput_sum = 0
a_throughput_list = []

n_throughput_sum = 0
n_throughput_list = []
for i in range(len(a3c_t)):

    a_throughput_sum += a3c_t.iloc[i]
    n_throughput_sum += new_t.iloc[i]
    count+=1
    if count == 203:
        count = 0
        a_throughput_list.append(a_throughput_sum/1000)
        n_throughput_sum = n_throughput_sum/1000
        n_throughput_list.append(n_throughput_sum)
        a_throughput_sum = 0
        n_throughput_sum = 0

game = [j for j in range(len(a_throughput_list))]

running_avg_1 = np.empty(len(a_throughput_list))
for t in range(len(a_throughput_list)):
    running_avg_1[t] = np.mean(a_throughput_list[max(0, t-5):(t+1)])

running_avg_2 = np.empty(len(n_throughput_list))
for t in range(len(n_throughput_list)):
    running_avg_2[t] = np.mean(n_throughput_list[max(0, t-5):(t+1)])

# plt.figure()
plt.plot(game, running_avg_1, label='A2C')
plt.plot(game, running_avg_2, label='NewReno')
plt.ylabel('Throughput (MBps)')
plt.xlabel('Episode')
plt.legend()
plt.savefig('throughput.png')

# plt.figure()
# plt.plot(game, running_avg_2, label='NewReno')
# plt.ylabel('Throughput (MBps)')
# plt.xlabel('Episode')
# plt.savefig('throughput_NewReno.png')
