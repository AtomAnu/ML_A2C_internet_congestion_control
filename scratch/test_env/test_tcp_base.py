#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from ns3gym import ns3env
from tcp_base import TcpNewReno, TcpTimeBased
# from actor_critic_discrete import Agent
from actor_critic_continuous import Agent
from utils import plotLearning
import csv
import math

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

port = 5556
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
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.dtype)

# a2c_agent = Agent(alpha=0.0001, beta=0.0005, input_dims=[4], gamma=0.99,
#                   n_actions=2, layer1_size=64, layer2_size=64)

tcp_agent = TcpNewReno()
# tcp_agent = TcpTimeBased()

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
throughput_history = []
rtt_history = []

obs_list = []

try:
    for i in range(iterationNum):
        obs = env.reset()

        obs_list.append(obs[4:])

        reward = 0
        done = False
        info = None
        # current_state = [obs[4]*0.0000000001,obs[6]*0.001,obs[11]*0.00001,obs[15]*0.001]
        score = 0
        throughput_sum = 0
        rtt_sum = 0

        while True:
            stepIdx += 1
            print(stepIdx)
            throughput_sum += obs[15]
            rtt_sum += obs[11]
            # action = a2c_agent.choose_action(current_state)
            action = tcp_agent.get_action(obs,reward,done)

            # print('ss type: {}'.format(type(action[0])))
            # print('cwnd type: {}'.format(type(action[1])))

            ssThresh = 680
            segmentSize = obs[6]
            if (obs[5] < ssThresh):
                # slow start
                if (obs[10] >= 1):
                    CWND = obs[5] + 340.0
                else:
                    CWND = obs[5]
            else:
                # congestion avoidance
                adder = 1.0 * (340**2) / obs[5]
                # adder = int(max(1.0, adder))
                CWND = obs[5] + adder

            print('Action: {}'.format(CWND))

            current_state_utility = math.log1p(obs[15]) - 0.0001*math.log1p(obs[11])

            # obs, reward, done, info = env.step([ssThresh, round(CWND,2)])
            # obs, reward, done, info = env.step([-10,action[1]])

            obs, reward, done, info = env.step([ssThresh, (CWND+ 1.11)])

            next_state_utility = math.log1p(obs[15]) - 0.0001*math.log1p(obs[11])

            reward = 0
            if next_state_utility - current_state_utility >= 0.9:
                reward = 100
            elif next_state_utility - current_state_utility <= -0.9:
                reward = -10

            obs_list.append(obs[4:])
            print('ssThresh: {}'.format(obs[4]))
            print('CWND: {}'.format(obs[5]))
            # next_state = [obs[4]*0.0000000001,obs[6]*0.001,obs[11]*0.00001,obs[15]*0.001]
            # reward = math.log1p(obs[15])-math.log1p(obs[11]*0.001)
            # print(reward)
            # a2c_agent.learn(current_state, reward, next_state, done)

            # print("---obs, reward, done, info: ", current_state, reward, done, info)
            print("---obs, reward, done, info: ", obs, reward, done, info)
            obs_list.append(obs[4:])
            # current_state = next_state
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
    filename = 'test_tcp_agent_NewReno.png'
    plotLearning(score_history, filename=filename, window=10)

    with open('reward_NewReno.csv', mode='w') as reward_file:
        csv_writer = csv.writer(reward_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(score_history)

    throughput_plot_filename = 'throughput_plot_NewReno.png'
    plotLearning(throughput_history, filename=throughput_plot_filename, window=10)

    rtt_plot_filename = 'rtt_plot_NewReno.png'
    plotLearning(rtt_history, filename=rtt_plot_filename, window=10)

    with open('network_obs_NewReno.csv', mode='w') as network_obs_file:
        csv_writer = csv.writer(network_obs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['ssThresh','CWND','segmentSize','bytesInFlightSum','bytesInFlightAvg','segmentsAckedSum',
                             'segmentsAckedAvg','avgRTT','minRTT','avgInterTx','avdInterRx','Throughput'])
        for i in range(len(obs_list)):
            # print(obs[i])
            csv_writer.writerow(obs_list[i])

    print("Done")


# //Ptr<OpenGymSpace> GetObservationSpace();
# //Ptr<OpenGymSpace> GetActionSpace();
# //Ptr<OpenGymDataContainer> GetObservation();
# //float GetReward();
# //bool GetGameOver();
# //std::string GetExtraInfo();
# //bool ExecuteActions(Ptr<OpenGymDataContainer> action);
#
# //#include "ns3/core-module.h"
# //#include "ns3/opengym-module.h"
# //
# //namespace ns3 {
# //
# //NS_LOG_COMPONENT_DEFINE ("openGym");
# //
# //NS_OBJECT_ENSURE_REGISTERED (openGym);
# //
# //
# //
# //}