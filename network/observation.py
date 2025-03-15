"""
This module provides the Observation class for pyModRev. The Observation class
encapsulates information about an observation, including the file path of the
observation data and the updater specified via the command line. It also
performs a basic check to ensure the provided observation file exists.
"""

import os
from updaters.updater import Updater


class Observation:
    """
    Represents an observation for the network model, including the file path
    of the observation data and the updater (as specified via the command line)
    """

    def __init__(self, observation_path: str, updater: Updater):
        """
        Initializes an Observation instance.
        """
        if not os.path.exists(observation_path):
            raise FileNotFoundError(f"Observation file not found: {observation_path}")
        self.observation_path = observation_path
        self.updater = updater

    def __str__(self):
        return f"Observation(path='{self.observation_path}', updater='{self.updater}')"

    def __repr__(self):
        return f"Observation(observation_path={self.observation_path!r}, updater={self.updater!r})"
