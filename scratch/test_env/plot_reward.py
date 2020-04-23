import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

a3c = pd.read_csv('network_obs_n_step.csv')
new = pd.read_csv('network_obs_10_step_og.csv')
reno = pd.read_csv('network_obs_NewReno.csv')

a3c_t = a3c[['Throughput']]
new_t = new[['Throughput']]
reno_t = reno[['Throughput']]

a3c_rtt = a3c[['avgRTT']]
new_rtt = new[['avgRTT']]
reno_rtt = reno[['avgRTT']]

count = 0
a_throughput_sum = 0
a_throughput_list = []

n_throughput_sum = 0
n_throughput_list = []

reno_throughput_sum = 0
reno_throughput_list = []

def calculate_reward(current_state, next_state):

    current_state_u = math.log1p(current_state[0]) - 0.0001*math.log1p(current_state[1])
    next_state_u = math.log1p(next_state[0]) - 0.0001 * math.log1p(next_state[1])
    reward = 0
    if next_state_u - current_state_u >= 0.9:
        reward = 100
    elif next_state_u - current_state_u <= -0.9:
        reward = -10

    return reward

for i in range(len(a3c_t)-1):
    print(i)
    a_reward = calculate_reward([a3c_t.iloc[i],a3c_rtt.iloc[i]],[a3c_t.iloc[i+1],a3c_rtt.iloc[i+1]])
    a_throughput_sum += a_reward
    n_reward = calculate_reward([new_t.iloc[i], new_rtt.iloc[i]], [new_t.iloc[i + 1], new_rtt.iloc[i + 1]])
    n_throughput_sum += n_reward
    reno_reward = calculate_reward([reno_t.iloc[i], reno_rtt.iloc[i]], [reno_t.iloc[i + 1], reno_rtt.iloc[i + 1]])
    reno_throughput_sum += reno_reward
    count+=1
    if count == 2000:
        count = 0
        a_throughput_list.append(a_throughput_sum)
        # n_throughput_sum = n_throughput_sum/(1000*200)
        n_throughput_list.append(n_throughput_sum)
        reno_throughput_list.append(reno_throughput_sum)
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
plt.ylabel('Total Reward')
plt.xlabel('Episode')
plt.legend()
plt.savefig('reward_comp.png')

# plt.figure()
# plt.plot(game, running_avg_2, label='NewReno')
# plt.ylabel('Throughput (MBps)')
# plt.xlabel('Episode')
# plt.savefig('throughput_NewReno.png')
