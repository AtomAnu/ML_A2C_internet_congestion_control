# Dynamic Internet Congestion Control using Deep Reinforcement Learning
Despite the state-of-art advancements of the internet, 
the same Transmission Control Protocol (TCP) has been employed for over three decades.
 TCP is a pre-configured rule-based algorithm designed to regulate how data of an application 
 should be broken into small data packets and sent through the network, partially alleviating 
 the problem of congestion. It is also responsible of handling lost or garbled packets by data re-transmission. Additionally, TCP algorithms have different pre-set goals, with some trying to maximise the throughput and some trying to minimise the queuing delay of the data transmission. This is due to thetrade-off between high throughput and low latency. The inefficacy of implementing such a rule-based TCP is its inability to perform well in handling congestion for diverse network usage scenarios.

In this research project, the concept of creating a dynamic congestion control algorithmis introduced. The algorithm will be design such that it oversees the sender side of the network.  The ideal congestion control design should be able to perceive the network structure and the level of congestion. Then, it should adjust the transmission rate for eachapplication dynamically so that fairness between applications is ensured. The algorithm should be refined to the optimal point where suitable throughput is maintained, and latency is minimised to an acceptable value. To create such a sophisticated design, the concept ofDeep Reinforcement Learning (DRL) is applied.

The main target of this research project is to create an agent with a dynamic congestion control algorithm that could outperform existing TCP algorithms used today. There are mainly two performance measures, system throughput and latency. Once trained, the performance of the agent should be compared against the performance of existing TCPs suchas NewReno, XCP and Vegas. This comparison can be done by deploying these agents,one at a time, in a uniform simulated network. The throughput, latency and any other measurements can then be obtained from the simulation.

A report describing this project can be found here.

# ns3gym Installation
# Runnning the training script for the A2C TCP Agent
