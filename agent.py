# python3
# Copyright 2018 DeepMind Technologies Limited. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""DQN agent implementation."""

import copy
from typing import NamedTuple

from acme import datasets
from acme import specs
from acme.adders import reverb as adders
from acme.agents import agent
from acme.agents.tf import actors
from acme.agents.tf.dqn import learning
from acme.tf import savers as tf2_savers
from acme.tf import utils as tf2_utils
from acme.utils import loggers
import reverb
import sonnet as snt
import tensorflow as tf
import trfl


class Save_paths(NamedTuple):
    data_dir: str
    experiment_name: str

class DQN(agent.Agent):
    """DQN agent.

    This implements a single-process DQN agent. This is a simple Q-learning
    algorithm that inserts N-step transitions into a replay buffer, and
    periodically updates its policy by sampling these transitions using
    prioritization.
    """

    def __init__(
            self,
            environment_spec: specs.EnvironmentSpec,
            network: snt.Module,
            params=None,
            logger: loggers.Logger = None,
            checkpoint: bool = True,
            paths: Save_paths = None,
    ):
        """Initialize the agent.

        Args:
          environment_spec: description of the actions, observations, etc.
          network: the online Q network (the one being optimized)
          batch_size: batch size for updates.
          prefetch_size: size to prefetch from replay.
          target_update_period: number of learner steps to perform before updating
            the target networks.
          samples_per_insert: number of samples to take from replay for every insert
            that is made.
          min_replay_size: minimum replay size before updating. This and all
            following arguments are related to dataset construction and will be
            ignored if a dataset argument is passed.
          max_replay_size: maximum replay size.
          importance_sampling_exponent: power to which importance weights are raised
            before normalizing.
          priority_exponent: exponent used in prioritized sampling.
          n_step: number of steps to squash into a single transition.
          epsilon: probability of taking a random action; ignored if a policy
            network is given.
          learning_rate: learning rate for the q-network update.
          discount: discount to use for TD updates.
          logger: logger object to be used by learner.
          checkpoint: boolean indicating whether to checkpoint the learner.
        """

        # Create a replay server to add data to. This uses no limiter behavior in
        # order to allow the Agent interface to handle it.
        if params is None:
            params = {
                'batch_size': 256,
                'prefetch_size': 4,
                'target_update_period': 100,
                'samples_per_insert': 32.0,
                'min_replay_size': 1000,
                'max_replay_size': 1000000,
                'importance_sampling_exponent': 0.2,
                'priority_exponent': 0.6,
                'n_step': 5,
                'epsilon': 0.05,
                'learning_rate': 1e-3,
                'discount': 0.99,
            }
        replay_table = reverb.Table(
            name=adders.DEFAULT_PRIORITY_TABLE,
            sampler=reverb.selectors.Prioritized(params['priority_exponent']),
            remover=reverb.selectors.Fifo(),
            max_size=params['max_replay_size'],
            rate_limiter=reverb.rate_limiters.MinSize(1))
        self._server = reverb.Server([replay_table], port=None)

        # The adder is used to insert observations into replay.
        address = f'localhost:{self._server.port}'
        adder = adders.NStepTransitionAdder(
            client=reverb.Client(address),
            n_step=params['n_step'],
            discount=params['discount'])

        # The dataset provides an interface to sample from replay.
        replay_client = reverb.TFClient(address)
        dataset = datasets.make_reverb_dataset(
            client=replay_client,
            environment_spec=environment_spec,
            batch_size=params['batch_size'],
            prefetch_size=params['prefetch_size'],
            transition_adder=True)

        # Use constant 0.05 epsilon greedy policy by default.
        epsilon = tf.Variable(params['epsilon'], trainable=False)

        policy_network = snt.Sequential([
            network,
            lambda q: trfl.epsilon_greedy(q, epsilon=epsilon).sample(),
        ])

        # Create a target network.
        target_network = copy.deepcopy(network)

        # Ensure that we create the variables before proceeding (maybe not needed).
        # tf2_utils.create_variables(network, [environment_spec.observations])
        # tf2_utils.create_variables(target_network, [environment_spec.observations])

        # Create the actor which defines how we take actions.
        actor = actors.FeedForwardActor(policy_network, adder)

        # The learner updates the parameters (and initializes them).
        learner = learning.DQNLearner(
            network=network,
            target_network=target_network,
            discount=params['discount'],
            importance_sampling_exponent=params['importance_sampling_exponent'],
            learning_rate=params['learning_rate'],
            target_update_period=params['target_update_period'],
            dataset=dataset,
            replay_client=replay_client,
            logger=logger,
            checkpoint=checkpoint)

        if checkpoint:
            self._checkpointer = tf2_savers.Checkpointer(
                add_uid=False,
                objects_to_save=learner.state,
                directory=paths.data_dir,
                subdirectory=paths.experiment_name,
                time_delta_minutes=60.)
        else:
            self._checkpointer = None

        super().__init__(
            actor=actor,
            learner=learner,
            min_observations=max(params['batch_size'], params['min_replay_size']),
            observations_per_step=float(params['batch_size']) / params['samples_per_insert'])

    def save(self):
        if self._checkpointer is not None:
            self._checkpointer.save(force=True)
            return self._checkpointer._checkpoint_manager.directory

    def update(self):
        super().update()
        if self._checkpointer is not None:
            self._checkpointer.save()
