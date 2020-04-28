#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#/usr/bin/python3

import argparse
from ns3gym import ns3env
from tcp_base import TcpTimeBased
from tcp_newreno import TcpNewReno
# from actor_critic_discrete import Agent
from actor_critic_continuous import NStepAgent
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
iterationNum = 100

port = 5555
simTime = 100 # seconds
seed = 12
simArgs = {"--duration": simTime,}
debug = False

env = ns3env.Ns3Env(port=port, startSim=startSim, simSeed=seed, simArgs=simArgs, debug=debug)

env.reset()

ob_space = env.observation_space
ac_space = env.action_space

print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.dtype)

a2c_agent = NStepAgent(alpha=5.19e-5, beta=2.42e-5, input_dims=[5], gamma=0.99,
                  n_actions=2, layer1_size=25, layer2_size=4)


stepIdx = 0
currIt = 0

score_history = []

action0_list = []
obs_list = []
throughput_history = []
rtt_history = []

cwnd_history = []

n_step = 200

try:
    for i in range(iterationNum):
        obs = env.reset()

        obs_list.append(obs[4:])

        reward = 0
        done = False
        info = None

        current_state = [obs[8]*0.00001,obs[9]*0.001,obs[11]*0.000001,obs[13]*(1/340)*0.0001,obs[14]*(1/340)*0.0001]
        score = 0
        throughput_sum = 0
        rtt_sum = 0

        nstep_td_counter = 0
        accum_reward = 0

        cwnd_history.append(obs[5])

        reward_list = []

        state_list = []
        while True:
            print("---obs, reward, done, info: ", current_state, reward, done, info)
            stepIdx += 1
            throughput_sum += obs[15]
            rtt_sum += obs[11]
            print(stepIdx)
            action = a2c_agent.choose_action(current_state)

            print('CWND increase: {}'.format(action[0]))

            print('action type: {}'.format(type(action[0])))

            action0_list.append(action[0])

            new_cwnd = obs[5] + action[0]
            if new_cwnd < 0.0:
                new_cwnd = 0.0
            elif new_cwnd > 65535.0:
                new_cwnd = 65535.0

            new_ssThresh = obs[4] + 0
            if new_ssThresh < 0:
                new_ssThresh = 0
            elif new_ssThresh > 65535:
                new_ssThresh = 65535

            current_state_utility = math.log1p(obs[15]) - 0.01*math.log1p(obs[11])

            obs, reward, done, info = env.step([new_ssThresh, new_cwnd])

            next_state_utility = math.log1p(obs[15]) - 0.01*math.log1p(obs[11])

            cwnd_history.append(obs[5])

            reward = 0
            # old value - 0.9
            if next_state_utility - current_state_utility >= 0.9:
                reward = 100
            elif next_state_utility - current_state_utility <= -0.9:
                reward = -10

            obs_list.append(obs[4:])

            reward = next_state_utility

            print('CWND: {}'.format(obs[5]))

            next_state = [obs[8]*0.00001,obs[9]*0.001,obs[11]*0.000001,obs[13]*(1/340)*0.0001,obs[14]*(1/340)*0.0001]

            state_list.append(current_state)
            reward_list.append(reward)

            if stepIdx < n_step:
                accum_reward += (a2c_agent.gamma ** (stepIdx-1)) * reward
            elif stepIdx == n_step:
                accum_reward += (a2c_agent.gamma ** (n_step-1)) * reward
                a2c_agent.learn(state_list[0], accum_reward, next_state, done, n_step)
                state_list.pop(0)
            else:
                accum_reward = (accum_reward - reward_list[0])/a2c_agent.gamma + ((a2c_agent.gamma ** (n_step-1)) * reward)
                a2c_agent.learn(state_list[0], accum_reward, next_state, done, n_step)
                state_list.pop(0)
                reward_list.pop(0)

            current_state = next_state
            score += reward

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
    filename = 'results/TCP_A2C_'+str(n_step)+'_step.png'
    plotLearning(score_history, filename=filename, window=10)

    with open('results/reward_'+str(n_step)+'_step.csv', mode='w') as reward_file:
        csv_writer = csv.writer(reward_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(score_history)

    throughput_plot_filename = 'results/throughput_plot_'+str(n_step)+'_step.png'
    plotLearning(throughput_history, filename=throughput_plot_filename, window=10)

    rtt_plot_filename = 'results/rtt_plot_'+str(n_step)+'_step.png'
    plotLearning(rtt_history, filename=rtt_plot_filename, window=10)

    print('obs_list: {}'.format(len(obs_list)))

    with open('results/network_obs_'+str(n_step)+'_step.csv', mode='w') as network_obs_file:
        csv_writer = csv.writer(network_obs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['ssThresh','CWND','segmentSize','bytesInFlightSum','bytesInFlightAvg','segmentsAckedSum',
                             'segmentsAckedAvg','avgRTT','minRTT','avgInterTx','avdInterRx','Throughput'])
        for i in range(len(obs_list)):
            csv_writer.writerow(obs_list[i])

    action0_list = sorted(action0_list)

    action0_freq = collections.Counter(action0_list)

    plt.figure()
    plt.plot(list(action0_freq),list(action0_freq.values()))
    plt.ylabel('Occurrence')
    plt.xlabel('Action')
    plt.savefig('results/action0_occurrence_'+str(n_step)+'_step.png')

    episode_number = [i for i in range(len(cwnd_history))]
    episode_number = [i/1999 for i in episode_number]
    plt.figure()
    plt.plot(episode_number, cwnd_history)
    plt.savefig('results/CWND_trend_'+str(n_step)+'_step.png')

    print("Done")

