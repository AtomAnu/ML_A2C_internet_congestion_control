#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#/usr/bin/python3

import argparse
from ns3gym import ns3env
from tcp_base import TcpTimeBased
from tcp_newreno import TcpNewReno
# from actor_critic_discrete import Agent
from actor_critic_continuous import Agent
from utils import plotLearning

import math
import csv
import matplotlib.pyplot as plt
import collections

parser = argparse.ArgumentParser(description='Start simulation script on/off')
parser.add_argument('--start',
                    type=int,
                    default=1,
                    help='Start ns-3 simulation script 0/1, Default: 1')
parser.add_argument('--iterations',
                    type=int,
                    default=1,
                    help='Number of iterations, Default: 1')
args = parser.parse_args()
startSim = bool(args.start)
# iterationNum = int(args.iterations)
iterationNum = 100

port = 5557
simTime = 100 # seconds
seed = 12
simArgs = {"--duration": simTime,}
debug = False

env = ns3env.Ns3Env(port=port, startSim=startSim, simSeed=seed, simArgs=simArgs, debug=debug)
# # simpler:
# env = ns3env.Ns3Env()
env.reset()

ob_space = env.observation_space
ac_space = env.action_space

# print('n_action: {}'.format(ac_space.n))

print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.dtype)

# a3c_agent = Agent(alpha=0.0001, beta=0.0005, input_dims=[12], gamma=0.99,
#                   n_actions=2, layer1_size=64, layer2_size=64)

# a2c_agent = Agent(alpha=0.0001, beta=0.0005, input_dims=[5], gamma=0.99,
#                   n_actions=2, layer1_size=64, layer2_size=64)

# original alpha = 5.19e-5
# beta=2.42e-5
a2c_agent = Agent(alpha=5.19e-5, beta=2.42e-5, input_dims=[5], gamma=0.99,
                  n_actions=2, layer1_size=64, layer2_size=64)

# print(a3c_agent)

stepIdx = 0
currIt = 0

def get_agent(obs):
    socketUuid = obs[0]
    tcpEnvType = obs[1]
    # print(tcpEnvType)
    tcpAgent = get_agent.tcpAgents.get(socketUuid, None)
    if tcpAgent is None:
        if tcpEnvType == 0:
            # event-based = 0
            tcpAgent = TcpNewReno()
        else:
            # time-based = 1
            tcpAgent = TcpTimeBased()
        tcpAgent.set_spaces(get_agent.ob_space, get_agent.ac_space)
        get_agent.tcpAgents[socketUuid] = tcpAgent

    return tcpAgent

# initialize variable
get_agent.tcpAgents = {}
get_agent.ob_space = ob_space
get_agent.ac_space = ac_space

score_history = []

action0_list = []
# action1_list = []
obs_list = []
throughput_history = []
rtt_history = []

cwnd_history = []

try:
    for i in range(iterationNum):
        obs = env.reset()

        obs_list.append(obs[4:])

        reward = 0
        done = False
        info = None
        current_state = [obs[8]*0.00001,obs[9]*0.001,obs[11]*0.000001,obs[13]*(1/340)*0.0001,obs[14]*(1/340)*0.0001]
        # print(current_state)
        score = 0
        throughput_sum = 0
        rtt_sum = 0

        nstep_td_counter = 0
        accum_reward = 0
        # starting_value = 500

        cwnd_history.append(obs[5])

        while True:
            print("---obs, reward, done, info: ", current_state, reward, done, info)
            stepIdx += 1
            throughput_sum += obs[15]
            rtt_sum += obs[11]
            print(stepIdx)
            # print('Current State: {}'.format(current_state))
            action = a2c_agent.choose_action(current_state)

            print('CWND increase: {}'.format(action[0]))
            # print('ssThresh increase: {}'.format(action[1]))

            # print('action 1 type: {}'.format(type(action[1])))

            action0_list.append(action[0])
            # action1_list.append(action[1])
            # print('Action 1 list length: {}'.format(len(action1_list)))

            # new_cwnd = (obs[5]+action[0]*10)*10
            new_cwnd = obs[5] + action[0]
            if new_cwnd < 0.0:
                new_cwnd = 0.0
            elif new_cwnd > 65535.0:
                new_cwnd = 65535.0

            # print('new_cwnd: {}'.format(new_cwnd))

            # new_ssThresh = obs[4]+action[1]*10
            # new_ssThresh = obs[4] + action[1]
            new_ssThresh = obs[4] + 0
            if new_ssThresh < 0:
                new_ssThresh = 0
            elif new_ssThresh > 65535:
                new_ssThresh = 65535

            # print('new_ssThresh: {}'.format(new_ssThresh))

            # current_state_utility = 10*math.log1p(obs[15])-5*math.log1p(obs[11])
            current_state_utility = math.log1p(obs[15]) - 0.01*math.log1p(obs[11])

            obs, reward, done, info = env.step([new_ssThresh, new_cwnd])

            # next_state_utility = 10 * math.log1p(obs[15]) - 5*math.log1p(obs[11])

            next_state_utility = math.log1p(obs[15]) - 0.01*math.log1p(obs[11])

            cwnd_history.append(obs[5])

            reward = 0
            # old value - 0.9
            if next_state_utility - current_state_utility >= 0.9:
                reward = 100
            elif next_state_utility - current_state_utility <= -0.9:
                reward = -10

            obs_list.append(obs[4:])

            print('CWND: {}'.format(obs[5]))
            print('ssThresh: {}'.format(obs[4]))

            next_state = [obs[8]*0.00001,obs[9]*0.001,obs[11]*0.000001,obs[13]*(1/340)*0.0001,obs[14]*(1/340)*0.0001]
            # next_state = [obs[11]*0.00001,obs[15]*0.001]
            # reward = 10*math.log1p(obs[15])-0.001*math.log1p(obs[11])

            # if nstep_td_counter < 100:
            #     accum_reward += 0.99**nstep_td_counter*reward
            #     if nstep_td_counter == 0:
            #         state = current_state
            #         state_ = next_state
            #     nstep_td_counter += 1
            # elif nstep_td_counter == 100:
            #     a2c_agent.learn(state, accum_reward, state_, done)
            #     nstep_td_counter = 0
            #     accum_reward = 0
            a2c_agent.learn(current_state, reward, next_state, done)

            # print("---obs, reward, done, info: ", current_state, reward, done, info)

            current_state = next_state
            score += reward

            # starting_value = 0

            if done:
                stepIdx = 0
                if currIt + 1 < iterationNum:
                    env.reset()
                break
        throughput_history.append(throughput_sum)
        rtt_history.append(rtt_sum)
        score_history.append(score)
        print('episode: ', i, 'score: %.2f' % score)


except KeyboardInterrupt:
    print("Ctrl-C -> Exit")
finally:
    env.close()
    filename = 'TCP_A2C.png'
    plotLearning(score_history, filename=filename, window=10)

    with open('reward_td0_step.csv', mode='w') as reward_file:
        csv_writer = csv.writer(reward_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(score_history)

    throughput_plot_filename = 'throughput_plot.png'
    plotLearning(throughput_history, filename=throughput_plot_filename, window=10)

    rtt_plot_filename = 'rtt_plot.png'
    plotLearning(rtt_history, filename=rtt_plot_filename, window=10)

    print('obs_list: {}'.format(len(obs_list)))
    # print('obs: {}'.format(obs_li[0][:]))

    with open('network_obs.csv', mode='w') as network_obs_file:
        csv_writer = csv.writer(network_obs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['ssThresh','CWND','segmentSize','bytesInFlightSum','bytesInFlightAvg','segmentsAckedSum',
                             'segmentsAckedAvg','avgRTT','minRTT','avgInterTx','avdInterRx','Throughput'])
        for i in range(len(obs_list)):
            # print(obs[i])
            csv_writer.writerow(obs_list[i])

    # print(action1_list)

    action0_list = sorted(action0_list)
    # action1_list = sorted(action1_list)

    # print(len(action1_list))

    action0_freq = collections.Counter(action0_list)
    # action1_freq = collections.Counter(action1_list)

    plt.figure()
    plt.plot(list(action0_freq),list(action0_freq.values()))
    plt.ylabel('Occurrence')
    plt.xlabel('Action')
    plt.savefig('action0_occurrence.png')

    # plt.figure()
    # plt.plot(list(action1_freq),list(action1_freq.values()))
    # plt.ylabel('Occurrence')
    # plt.xlabel('Action')
    # plt.savefig('action1_occurrence.png')

    episode_number = [i for i in range(len(cwnd_history))]
    episode_number = [i/1999 for i in episode_number]
    plt.figure()
    plt.plot(episode_number, cwnd_history)
    plt.savefig('CWND Trend')


    # print(list(action1_freq))
    # print(list(action1_freq.values()))
    #
    # print(action0_freq)

    print("Done")

