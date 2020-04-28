# Dynamic Internet Congestion Control using Deep Reinforcement Learning
Rapid increase in the internet usage has proliferated the demand for data transmission over the networks around the world. In other words, the traffic over internet has become significantly more congested in recent years. As a consequence, the network latency and the number of lost or dropped packets of data have risen above the acceptable levels. Current Transmission Control Protocol (TCP) algorithms have been performing reasonably well in regulating the flow of data across networks to reduce congestion but lack the dynamic aspect to deal with today’s fast-changing network environments. This research project seeks to develop a dynamic congestion control algorithm by developing a Deep Reinforcement Learning agent with the Advantage Actor-Critic (A2C) structure.

Despite the state-of-art advancements of the internet, 
the same Transmission Control Protocol (TCP) has been employed for over three decades.
 TCP is a pre-configured rule-based algorithm designed to regulate how data of an application 
 should be broken into small data packets and sent through the network, partially alleviating 
 the problem of congestion. It is also responsible of handling lost or garbled packets by data re-transmission. Additionally, TCP algorithms have different pre-set goals, with some trying to maximise the throughput and some trying to minimise the queuing delay of the data transmission. This is due to the trade-off between high throughput and low latency. The inefficacy of implementing such a rule-based TCP is its inability to perform well in handling congestion for diverse network usage scenarios.

In this research project, the concept of creating a dynamic congestion control algorithm is introduced. The algorithm will be design such that it oversees the sender side of the network.  The ideal congestion control design should be able to perceive the network structure and the level of congestion. Then, it should adjust the transmission rate for each application dynamically so that fairness between applications is ensured. The algorithm should be refined to the optimal point where suitable throughput is maintained, and latency is minimised to an acceptable value. To create such a sophisticated design, the concept ofDeep Reinforcement Learning (DRL) is applied.

The main target of this research project is to create an agent with a dynamic congestion control algorithm that could outperform existing TCP algorithms used today. There are mainly two performance measures, system throughput and latency. Once trained, the performance of the agent should be compared against the performance of existing TCPs suchas NewReno, XCP and Vegas. This comparison can be done by deploying these agents,one at a time, in a uniform simulated network. The throughput, latency and any other measurements can then be obtained from the simulation.

A report fully describing this project can be found [here](./Final-Report.pdf).

# ns3gym Installation
This project uses the `ns3gym` package create in this [repository](https://github.com/tkn-tub/ns3-gym). In order to run the training script for the A2C TCP Agent, this package needs to installed first. The instruction on how to install this package can be found [here](./setup_guide/SETUP_GUIDE.md).

# Runnning the training scripts for the A2C TCP Agent
The directory of the code related to the development of the A2C TCP Agent can be found [here](./scratch/A2C_TCP). There are two training scripts in this directory. The first training script `td0_agent_train.py` (found [here](./scratch/td0_agent_train.py) trains the agent that adopts the Temporal-Difference Learning (TD(0)) method. The second script `n_step_td_agent_train.py` (found [here](./scratch/n_step_td_agent_train.py)) trains the agent that adopts the n-step Temporal-Difference Learning method.
