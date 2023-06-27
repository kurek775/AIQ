"""
VPG agent modified from minimalistic implementation of Vanilla Policy Gradient by Leonardo Barazza known as Ibarazza on Github
@link{https://github.com/lbarazza/VPG-PyTorch}
This agent was modified for use on specifically Discrete and interactive (non-gym) based environment of AIQ.

Original Author: Leonardo Barazza 2019
Modified By: Petr Zeman 2022
"""

from .Agent import Agent
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from collections import deque

# define policy network
class policy_net(nn.Module):
    def __init__(self, nS, nH, nA): # nS: state space size, nH: n. of neurons in hidden layer, nA: size action space
        super(policy_net, self).__init__()
        self.h = nn.Linear(nS, nH)
        self.out = nn.Linear(nH, nA)

    # define forward pass with one hidden layer with ReLU activation and sofmax after output layer
    def forward(self, x):
        x = F.relu(self.h(x))
        x = F.softmax(self.out(x), dim=1)
        return x


class IbaVPG(Agent):

    def __init__( self, refm, disc_rate, steps_per_epoch =  10, gamma = 0.99 ):
        Agent.__init__( self, refm, disc_rate )

        self.steps_per_epoch = steps_per_epoch
        self.num_states  = refm.getNumObs() # assuming that states = observations
        self.obs_symbols = refm.getNumObsSyms()
        self.obs_cells   = refm.getNumObsCells()
        self.obs_dim = refm.getNumObsSyms() * refm.getNumObsCells()
        self.act_dim = refm.getNumActions()

        self.policy = policy_net(self.obs_dim, 32, self.act_dim)
        # create an optimizer
        self.optimizer = torch.optim.Adam(self.policy.parameters())

        # initialize gamma and stats
        self.gamma = gamma
        self.n_episode = 1
            
        self.reset()


    def reset( self ):

        # Reset state and action
        self.state  = 0
        self.action = 0
        self.epoch_step = 0

        self.rewards = []
        self.actions = []
        self.states = []

        # Set up model saving
        # logger.setup_pytorch_saver(ac)


    def __str__( self ):
        return "IbaVPG(" + ")"


    def update(self):
        # preprocess rewards
        self.rewards = np.array(self.rewards)
        # calculate rewards to go for less variance
        R = torch.tensor(
            [np.sum(self.rewards[i:] * (self.gamma ** np.array(range(i, len(self.rewards))))) for i in range(len(self.rewards))])
        # or uncomment following line for normal rewards
        # R = torch.sum(torch.tensor(rewards))

        # preprocess states and actions
        self.states = torch.tensor(np.array(self.states)).float()[:,-1,:]
        self.actions = torch.tensor(self.actions).float()

        # calculate gradient
        self.probs = self.policy(self.states)
        self.sampler = Categorical(self.probs)
        log_probs = -self.sampler.log_prob(self.actions)  # "-" because it was built to work with gradient descent, but we are using gradient ascent
        pseudo_loss = torch.sum(log_probs * R)  # loss that when differentiated with autograd gives the gradient of J(θ)
        # update policy weights
        self.optimizer.zero_grad()
        pseudo_loss.backward()
        self.optimizer.step()
        self.rewards = []
        self.actions = []
        self.states = []



    def perceive( self, observations, reward ):

        if len(observations) != self.obs_cells:
            raise NameError("VPG recieved wrong number of observations!")

        # convert observations into a single number for the new state
        nstate = 0
        for i in range(self.obs_cells):
           nstate = observations[i] * self.obs_symbols**i


        # if(observations[0]>5):
        #     print("Chyba v hodnotě: " + str(observations[0]))
        # print(str(observations))
        observation_index = observations[0]
        np_observation_list = np.array(nstate)
        try:
            # np_observation_current = torch.from_numpy(np_observation_list).float().unsqueeze(0)
            np_observation_current: np.ndarray = np.eye(self.obs_dim)[np_observation_list.reshape(-1)]
            # np_observation_current = np_observation_list.reshape((self.obs_dim,) + (1,))
        except IndexError as e:
            print("Chyba v hodnotě: " + str(observations[0]))


        # calculate probabilities of taking each action
        self.probs = self.policy(torch.tensor(np_observation_current).float())
        # self.probs = self.policy(torch.tensor(nstate).unsqueeze(0).float())
        # sample an action from that set of probs
        self.sampler = Categorical(self.probs)
        action = self.sampler.sample()

        # store state, action and reward
        self.states.append((np_observation_current))
        # self.states.append(nstate)
        # action_tensor: np.ndarray = np.eye(self.act_dim)[action.reshape(-1)]
        # action_tensor = torch.tensor(action)
        one_hot_action: np.ndarray = np.eye(self.act_dim)[np.array(action.item()).reshape(-1)]
        self.actions.append(action)
        self.rewards.append(reward)

        if (self.epoch_step == self.steps_per_epoch-1):
            self.update()
            self.epoch_step =0
        else:
            self.epoch_step += 1


        return action.item()

