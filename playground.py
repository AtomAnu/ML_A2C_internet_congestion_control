# import random
# import matplotlib.pyplot as plt
#
# normSamples = [random.expovariate(1) for i in range(100000)]
# fig, axis = plt.subplots()
# axis.hist(normSamples, bins=100, density=True)
# axis.set_title(r"Histogram of an Normal RNG $\mu = 9$ and $\sigma = 2$")
# axis.set_xlabel("x")
# axis.set_ylabel("normalized frequency of occurrence")
# plt.show()

import gym

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

env = gym.make('CartPole-v1')
# Optional: PPO2 requires a vectorized environment to run
# the env is now wrapped automatically when passing it to the constructor
env = DummyVecEnv([lambda: env])

model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=1000)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()

# model = PPO2(MlpPolicy, 'CartPole-v1', verbose=1).learn(1000)