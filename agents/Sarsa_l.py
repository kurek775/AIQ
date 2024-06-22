#
# Sarsa algorithm for Sutton and Barto page 184
#
# Copyright Shane Legg 2011
# Released under GNU GPLv3
#

from .Agent import Agent
from numpy import zeros, ones
import numpy as np
from random import randint, randrange, random
import sys
import os
from agents.utils.spinning_up_tools.logx import EpochLogger
from .utils.observation_encoder import encode_observations_int


class Sarsa_l(Agent):

    def __init__(self, refm, disc_rate, init_Q, Lambda, alpha, epsilon, gamma=0):

        Agent.__init__(self, refm, disc_rate)

        self.num_states = refm.getNumObs()  # assuming that states = observations
        self.obs_symbols = refm.getNumObsSyms()
        self.obs_cells = refm.getNumObsCells()

        self.init_Q = init_Q
        self.Lambda = Lambda
        self.epsilon = epsilon
        self.alpha = alpha
        self.logger = dict()

        # if the internal discount rate isn't set, use the environment value
        if gamma == 0:
            self.gamma = disc_rate
        else:
            self.gamma = gamma

        if self.gamma >= 1.0:
            print(
                "Error: Sarsa_l can only handle an internal discount rate ",
                "that is below 1.0",
            )
            sys.exit()

        self.divergence_limit = 100 * (1 + self.Lambda) / (1 - self.gamma)

        self.reset()

    def reset(self):
        self.state = 0
        self.action = 0
        self.logger = dict()
        self.failed = False

        self.Q_value = self.init_Q * ones((self.num_states, self.num_actions))
        self.E_trace = zeros((self.num_states, self.num_actions))
        self.visits = zeros((self.num_states))

    def __str__(self):
        return (
            "Sarsa_l("
            + str(self.init_Q)
            + ","
            + str(self.Lambda)
            + ","
            + str(self.alpha)
            + ","
            + str(self.epsilon)
            + ","
            + str(self.gamma)
            + ")"
        )

    def perceive(self, observations, reward):

        if len(observations) != self.obs_cells:
            raise NameError("Sarsa_l recieved wrong number of observations!")

        # convert observations into a single number for the new state
        nstate = encode_observations_int(observations, self.obs_symbols)

        # set up alisas
        Q = self.Q_value
        E = self.E_trace
        gamma = self.gamma

        # find an optimal action according to current Q values
       
        # action selection
        if self.sel_mode == 0:
            # do an epsilon greedy selection
            if random() < self.epsilon:
                naction = randrange(self.num_actions)
            else:
                 naction = self.soft_max(Q[nstate], self.epsilon)
        # update Q values using old state, old action, reward, new state and next action
        delta_Q = reward + gamma * Q[nstate, naction] - Q[self.state, self.action]
        q_value = Q[self.state, self.action]
        e_value = E[self.state, self.action]
        self.log_update(q_value,e_value,self.state,self.action)
        E[self.state, self.action] += 1
        for s in range(self.num_states):
            for a in range(self.num_actions):
                Q[s, a] = Q[s, a] + self.alpha * delta_Q * E[s, a]
                E[s, a] = E[s, a] * gamma * self.Lambda
                
                # Q value suggests a soft divergence occured
                if Q[s, a] > self.divergence_limit or Q[s, a] < -self.divergence_limit:
                    self.failed = True

        # update the old action and state
        self.state = nstate
        self.action = naction

        return naction

    def log_update(self, Q, E,s,a):
        self.logger.update(
            {"Q_value": Q, "E_trace":E, "state": s, "action": a}
        )

    def get_logs(self) -> dict:
        return self.logger
