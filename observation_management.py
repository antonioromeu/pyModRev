import subprocess
import json
from colomoto_jupyter.sessionfiles import new_output_file
from ginsim.gateway import japi
import biolqm
from asp_helper import ASPHelper


def reduce_to_prime_implicants(lqm):
    # BioLQM.ModRevExport outputs the prime implicants
    exported_model_file = save(lqm)
    return biolqm.load(exported_model_file, "lp")

def save(model, format="lp"):
    filename = new_output_file(format)
    return biolqm.save(model, filename, format)

def save_observations_to_lp(formatted_obs: list, file_path: str):
    exp_entries = [obs for obs in formatted_obs if obs.startswith("exp(")]
    other_entries = [obs for obs in formatted_obs if not obs.startswith("exp(")]

    with open(file_path, "w") as lp_file:
        lp_file.write("\n".join(exp_entries + other_entries) + "\n")


class PyModRev:
    def __init__(self, model_path: str):
        """
        Initialize the model revision tool with a given network model.
        """
        self.network = self.load(model_path)
        # ss obs_name [0, 1, "*", 1, 0]
        # sy obs_name [[0, 1, 1, 0], [[0, 1, 1, 1]]
        # ss obs_name {node_name_1: node_value_1, node_name_2: node_value_2}
        # sy obs_name {time_step_1: {node_name_1: node_value_1, node_name_2: node_value_2}, time_step_2: {node_name_1: node_value_1, node_name_2: node_value_2}}
        # as obs_name {time_step_1: {node_name_1: node_value_1, node_name_2: node_value_2}, time_step_2: {node_name_1: node_value_1, node_name_2: node_value_2}}
        # co obs_name {time_step_1: {node_name_1: node_value_1, node_name_2: node_value_2}, time_step_2: {node_name_1: node_value_1, node_name_2: node_value_2}}
        self.observations = {}
        # self.prime_implicantes = None
        self.inconsistent_solutions = []
        self.experiments = set()

    def load(self, model_path: str):
        """
        Load the model from a given path.
        """
        return reduce_to_prime_implicants(model_path)

    def is_consistent(self) -> bool:
        """
        Check if the model is consistent.
        """
        self.inconsistent_solutions, optimization = ASPHelper.check_consistency(self.network)
        return optimization == 0

    def format_observations(self):
        """
        Format all observations stored in self.observations.
        """
        formatted_obs = []
        experiences = set()
        for obs_name, (obs_type, obs_data) in self.observations.items():
            if obs_name not in experiences:
                formatted_obs.append(f"exp({obs_name}).")
                experiences.add(obs_name)
            if obs_type == "ss":
                for node, value in obs_data.items():
                    formatted_obs.append(f"obs_vlabel({obs_name},{node},{value}).")
            else:
                for time_step, node_values in obs_data.items():
                    for node, value in node_values.items():
                        formatted_obs.append(f"obs_vlabel({obs_name},{time_step},{node},{value}).")
        return formatted_obs

    def obs_add(self, obs_type: str, obs_name: str, obs_data):
        """
        Add an observation to the model.
        """
        if obs_type not in ["ss", "sy", "as", "co"]:
            raise ValueError("Invalid observation type.")
        self.observations[obs_name] = (obs_type, obs_data)

    def obs_remove(self, name: str = None):
        """
        Remove an observation by name or all if no name is provided.
        """
        if name:
            self.observations.pop(name, None)
        else:
            self.observations.clear()

    def obs_list(self, obs_name: str = None):
        """
        List observations, optionally filtering by name.
        """
        return self.observations if not obs_name else {name: self.observations.get(obs_name)}
