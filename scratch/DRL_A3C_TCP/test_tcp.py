#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from ns3gym import ns3env
from tcp_base import TcpTimeBased
from tcp_newreno import TcpNewReno
# from actor_critic_discrete import Agent
from actor_critic_continuous import Agent
from utils import plotLearning

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
iterationNum = 2

port = 5555
simTime = 1000 # seconds
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

a3c_agent = Agent(alpha=0.0001, beta=0.0005, input_dims=[12], gamma=0.99,
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

try:
    while True:
        # print("Start iteration: ", currIt)
        obs = env.reset()
        reward = 0
        done = False
        info = None
        # print("Step: ", stepIdx)
        # print("---obs: ", obs[4:])

        # get existing agent of create new TCP agent if needed
        tcpAgent = get_agent(obs)

        ###########
        current_state = obs[4:]
        ###########

        score = 0

        while True:
            # print(env.get_random_action()[0])
            stepIdx += 1
            # action = tcpAgent.get_action(obs, reward, done, info)
            action = a3c_agent.choose_action(current_state)
            # print("---action: ", action)

            # print("Step: ", stepIdx)
            obs, reward, done, info = env.step(action)
            ###########
            next_state = obs[4:]
            reward = obs[15]-obs[11]*0.001
            # print(obs[11]*0.001)
            # print(reward)
            a3c_agent.learn(current_state, reward, next_state, done)
            ###########
            # print(len(obs))
            print("---obs, reward, done, info: ", current_state, reward, done, info)

            # get existing agent of create new TCP agent if needed
            # tcpAgent = get_agent(obs)

            current_state = next_state

            score += reward

            if done:
                stepIdx = 0
                if currIt + 1 < iterationNum:
                    env.reset()
                break
        score_history.append(score)
        currIt += 1
        if currIt == iterationNum:
            break

except KeyboardInterrupt:
    print("Ctrl-C -> Exit")
finally:
    env.close()
    filename = 'TCP_A2C.png'
    plotLearning(score_history, filename=filename, window=20)
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