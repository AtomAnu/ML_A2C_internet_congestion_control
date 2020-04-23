import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

class GenericNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims,
                 n_actions):
        super(GenericNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self.n_actions)
        self.optimizer = optim.Adam(self.parameters(), lr=alpha)
        # self.optimizer = T.optim.SGD(self.parameters(), lr=alpha)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu:0')
        self.to(self.device)

    def forward(self, observation):
        state = T.tensor(observation, dtype=T.float).to(self.device)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x

class ComplexNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims,
                 n_actions):
        super(ComplexNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self.n_actions)
        self.optimizer = optim.Adam(self.parameters(), lr=alpha)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu:0')
        self.to(self.device)

    def forward(self, observation):
        state = T.tensor(observation, dtype=T.float).to(self.device)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x

class ActorCriticNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims,
                 n_actions):
        super(ActorCriticNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.pi = nn.Linear(self.fc2_dims, self.n_actions)
        self.v = nn.Linear(self.fc2_dims, 1)
        self.optimizer = optim.Adam(self.parameters(), lr=alpha)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu:0')
        self.to(self.device)

    def forward(self, observation):
        state = T.tensor(observation, dtype=T.float).to(self.device)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        pi = self.pi(x)
        v = self.v(x)

        return pi, v

class Agent(object):
    def __init__(self, alpha, beta, input_dims, gamma=0.99, n_actions=2,
                 layer1_size=256, layer2_size=256, n_outputs=1):
        self.gamma = gamma
        self.log_probs = None
        self.n_outputs = n_outputs
        self.actor = GenericNetwork(alpha, input_dims, layer1_size,
                                           layer2_size, n_actions=n_actions)
        self.critic = GenericNetwork(beta, input_dims, layer1_size,
                                            layer2_size, n_actions=1)

    def choose_action(self, observation):
        mu, sigma  = self.actor.forward(observation).to(self.actor.device)
        # sigma = self.actor.forward(observation)  # .to(self.actor.device)
        print(type(sigma))
        sigma = sigma.clamp(-10,10)
        print("Mu: {}".format(mu))
        print("Sigma: {}".format(sigma))
        sigma = T.exp(sigma)
        print("NEW Sigma: {}".format(sigma))
        action_probs = T.distributions.Normal(mu, sigma.float(), validate_args=True)
        # action_probs = T.distributions.Exponential(rate=1/sigma, validate_args=True)
        probs = action_probs.sample(sample_shape=T.Size([self.n_outputs]))
        self.log_probs = action_probs.log_prob(probs).to(self.actor.device)
        # action = T.tanh(probs)
        action = probs

        return [round(action.item(),2)]
        # return [round(action[0].item(),2),int(action[1].item())]

    def learn(self, state, reward, new_state, done):
        critic_value_ = self.critic.forward(new_state)
        critic_value = self.critic.forward(state)
        reward = T.tensor(reward, dtype=T.float).to(self.actor.device)
        #delta = ((reward + self.gamma*critic_value_*(1-int(done))) -critic_value)
        delta = ((reward + self.gamma ** 20 * critic_value_ * (1 - int(done))) - critic_value)

        actor_loss = -self.log_probs * delta
        # actor_loss_1 = -self.log_probs[0] * delta * 0.5
        # actor_loss_2 = -self.log_probs[1] * delta * 0.5
        # actor_loss_1 = self.log_probs[0] * delta * 0.5
        # actor_loss_2 = self.log_probs[1] * delta * 0.5
        critic_loss = delta**2

        self.actor.optimizer.zero_grad()
        (actor_loss).backward(retain_graph = True)
        self.actor.optimizer.step()
        self.critic.optimizer.zero_grad()
        # (actor_loss_1 + actor_loss_2 + critic_loss).backward()
        (critic_loss).backward()
        self.critic.optimizer.step()

class NewAgent(object):
    def __init__(self, alpha, beta, input_dims, gamma=0.99, n_actions=2,
                 layer1_size=256, layer2_size=256, n_outputs=2):
        self.gamma = gamma
        self.log_probs = None
        self.n_outputs = n_outputs
        self.actor_critic = ActorCriticNetwork(alpha, input_dims, layer1_size,
                                        layer2_size, n_actions=n_actions)

    def choose_action(self, observation):
        pi, v = self.actor_critic.forward(observation)

        mu, sigma = pi
        sigma = T.exp(sigma)
        action_probs = T.distributions.Normal(mu, sigma)
        probs = action_probs.sample(sample_shape=T.Size([self.n_outputs]))
        self.log_probs = action_probs.log_prob(probs).to(self.actor_critic.device)
        action = T.tanh(probs)

        return action.item()

    def learn(self, state, reward, new_state, done):
        self.actor_critic.optimizer.zero_grad()

        _, critic_value_ = self.actor_critic.forward(new_state)
        _, critic_value = self.actor_critic.forward(state)

        reward = T.tensor(reward, dtype=T.float).to(self.actor_critic.device)
        delta = reward + self.gamma*critic_value_*(1-int(done)) - critic_value

        actor_loss = -self.log_probs * delta
        critic_loss = delta**2

        (actor_loss + critic_loss).backward()

        self.actor_critic.optimizer.step()
