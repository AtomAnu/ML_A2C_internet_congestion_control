"""
Simple example of PacketGenerator and PacketSink from the SimComponents module.
Creates two constant rate packet generators and wires them to one sink.
Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort, PortMonitor


def constArrival():  # Constant arrival distribution for generator 1
    return 1.5

def constArrival2():
    return 2.0

def distSize():
    # randomly select a number for an exponential distribution
    return expovariate(0.01)

if __name__ == '__main__':
    env = simpy.Environment()  # Create the SimPy environment
    # Create the packet generators and sink
    pg = PacketGenerator(env, "EE283", constArrival, distSize)
    ps = PacketSink(env, debug=True)  # debugging enable for simple output
    sp = SwitchPort(env, rate=200.0)
    # Wire packet generators and sink together
    pg.out = sp
    sp.out = ps
    env.run(until=20) # Run it
    print(ps.waits)
