import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

a3c = pd.read_csv('network_obs_n_step.csv')
new = pd.read_csv('network_obs_1_step.csv')
reno = pd.read_csv('network_obs_NewReno.csv')

a3c_t = a3c[['Throughput']]

print(a3c_t)
new_t = new[['Throughput']]
reno_t = reno[['Throughput']]

count = 0
a_throughput_sum = 0
a_throughput_list = []

n_throughput_sum = 0
n_throughput_list = []

reno_throughput_sum = 0
reno_throughput_list = []
for i in range(len(a3c_t)):
    print(i)
    a_throughput_sum += a3c_t.iloc[i]
    n_throughput_sum += new_t.iloc[i]
    reno_throughput_sum += reno_t.iloc[i]
    count+=1
    if count == 2000:
        count = 0
        a_throughput_list.append(a_throughput_sum/(1000*100))
        n_throughput_sum = n_throughput_sum/(1000*100)
        n_throughput_list.append(n_throughput_sum)
        reno_throughput_list.append(reno_throughput_sum/(1000*10))
        a_throughput_sum = 0
        n_throughput_sum = 0
        reno_throughput_sum = 0

game = [j for j in range(len(a_throughput_list))]

running_avg_1 = np.empty(len(a_throughput_list))
for t in range(len(a_throughput_list)):
    running_avg_1[t] = np.mean(a_throughput_list[max(0, t-5):(t+1)])

running_avg_2 = np.empty(len(n_throughput_list))
for t in range(len(n_throughput_list)):
    running_avg_2[t] = np.mean(n_throughput_list[max(0, t-5):(t+1)])

running_avg_3 = np.empty(len(reno_throughput_list))
for t in range(len(reno_throughput_list)):
    running_avg_3[t] = np.mean(reno_throughput_list[max(0, t-5):(t+1)])

# plt.figure()
plt.plot(game, running_avg_1, label='TD(0)')
plt.plot(game, running_avg_2, label='10-step TD')
plt.plot(game, running_avg_3, label='NewReno')
plt.ylabel('Average Throughput (MBps)')
plt.xlabel('Episode')
plt.legend()
plt.savefig('throughput_comp.png')

# plt.figure()
# plt.plot(game, running_avg_2, label='NewReno')
# plt.ylabel('Throughput (MBps)')
# plt.xlabel('Episode')
# plt.savefig('throughput_NewReno.png')
