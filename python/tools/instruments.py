import os
from ..tools import file

BASE_DIR = os.environ.get("BASE_DIR", "./agent_results")

class AgentInstruments:
    """
    Base class for multli-agent instruments that are tools, state, and functions that an agent can use across the lifecycle of conversations
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.messages = []
        self.innovation_index = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def sync_messages(self, messages: list):
        """
        Syncs messages with the orchestrator
        """
        self.messages = messages

    def reset_files(self):
        """
        Clear everything in the root_dir
        """

        # if it does not exist create it
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

        for fname in os.listdir(self.root_dir):
            os.remove(os.path.join(self.root_dir, fname))
    
    def get_file_path(self, fname: str):
        """
        Get the full path to a file in the root_dir
        """
        return os.path.join(self.root_dir, fname)
    
    # -------------------------- Agent Functions -------------------------- #

    def write_file(self, content: str):
        fname = self.get_file_path(f"write_file.txt")
        return file.write_file(fname, content)

    def write_json_file(self, json_str: str):
        fname = self.get_file_path(f"write_json_file.json")
        return file.write_json_file(fname, json_str)

    def write_yml_file(self, json_str: str):
        fname = self.get_file_path(f"write_yml_file.yml")
        return file.write_yml_file(fname, json_str)

    def write_innovation_file(self, content: str):
        fname = self.get_file_path(f"{self.innovation_index}_innovation_file.json")
        file.write_file(fname, content)
        self.innovation_index += 1
        return f"Successfully wrote innovation file. You can check my work."

    def validate_innovation_files(self):
        """
        loop from 0 to innovation_index and verify file exists with content
        """
        for i in range(self.innovation_index):
            fname = self.get_file_path(f"{i}_innovation_file.json")
            with open(fname, "r") as f:
                content = f.read()
                if not content:
                    return False, f"File {fname} is empty"

        return True, ""

    def make_agent_chat_file(self, team_name: str):
        return os.path.join(self.root_dir, f"agent_chats_{team_name}.json")

    def make_agent_cost_file(self, team_name: str):
        return os.path.join(self.root_dir, f"agent_cost_{team_name}.json")

    @property
    def root_dir(self):
        return os.path.join(BASE_DIR, self.session_id)