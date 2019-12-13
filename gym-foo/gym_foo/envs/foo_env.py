import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np

class FooEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
      self.action_space = spaces.Box(np.array([-1e12, -1e12]), np.array([1e12, 1e12]), dtype=np.float32)


obj = FooEnv()
print(type(obj.action_space))

  # def step(self, action):
  # def reset(self):
  # def render(self, mode='human', close=False):