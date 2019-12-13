import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

class GenericNetwork(nn.Module):
    """
    Class for the networks of the actor and the critic.
    """

    def __init__(self, lr, input_dims, fc1_dims, fc2_dims, n_actions):
        """
        Initializer

        :param lr: learning rate
        :param input_dims: input dimension of the environment
        :param fc1_dims: dimension of the first layer
        :param fc2_dims: dimension of the second layer
        :param n_actions: number of actions in the environment
        """

        super(GenericNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.lr = lr

        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self. n_actions)

        #Adam optimizer to train the network
        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu:0')
        self.to(self.device)

    def forward(self, observation):
        """
        Feed-forward function

        :param observation: environment observation (numpy array)
        :return:
        """

        #Cuda tensor
        state = T.Tensor(observation).to(self.device)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x

class Agent(object):
    """
    Agent containing one actor and one critic
    """
    def __init__(self, alpha, beta, input_dims, gamma=0.99, l1_size=256,
                 l2_size = 256, n_actions=2):
        """
        Initializer

        :param alpha: learning rate for ACTOR
        :param beta: learning rate for CRITIC
        :param input_dims: input dimension of the environment
        :param gamma: discount rate of rewards
                      (present rewards should be more valuable than past rewards)
        :param l1_size: layer 1 dimension
        :param l2_size: layer 2 dimension
        :param n_actions: number of actions
        """

        self.gamma = gamma

        #actor-critic method updates the actor network with the gradient of the log of the policy (log probability)
        self.log_probs = None

        self.actor = GenericNetwork(alpha, input_dims, l1_size, l2_size, n_actions)
        self.critic = GenericNetwork(beta, input_dims, l1_size, l2_size, n_actions=1)

    def choose_action(self, observation):

        #probabilities should add up to one -> use softmax
        probabilities = F.softmax(self.actor.forward(observation))
        action_probs = T.distributions.Categorical(probabilities)
        action = action_probs.sample()
        self.log_probs = action_probs.log_prob(action)

        #action is a tensor while openai gym takes integer so use action.item() instead
        return action.item()

    def learn(self, state, reward, new_state, done):
        self.actor.optimizer.zero_grad()
        self.critic.optimizer.zero_grad()

        critic_value = self.critic.forward(state)
        critic_value_ = self.critic.forward(new_state)

        #calculate the temporal difference
        delta = (reward + self.gamma*critic_value_*(1-int(done)) - critic_value)

        actor_loss = -self.log_probs * delta
        critic_loss = delta**2

        (actor_loss + critic_loss).backward()

        self.actor.optimizer.step()
        self.critic.optimizer.step()
