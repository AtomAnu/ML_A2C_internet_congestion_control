import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np

from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort, PortMonitor

class FooEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Box(np.array([-1e12, -1e12]), np.array([1e12, 1e12]), dtype=np.float32)

    def constArrival():  # Constant arrival distribution for generator 1
        return 1.5

    def constArrival2():
        return 2.0

    def distSize():
        # randomly select a number for an exponential distribution
        return expovariate(0.01)

    def construct_network(self):
        rate = 200.0

        #construct each component of the network system
        env = simpy.Environment()
        pg1 = PacketGenerator(env, "GEN001", constArrival, distSize)
        ps1 = PacketSink(env, debug=True)
        sp = SwitchPort(env, rate=rate)

        #connect the components together
        pg1.out = sp
        sp.out = ps1

  # def step(self, action):
  # def reset(self):
  # def render(self, mode='human', close=False):