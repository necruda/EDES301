"""
--------------------------------------------------------------------------
Project Manager
--------------------------------------------------------------------------
"""
import os
import json

class ProjectManager:
    def __init__(self, directory="/var/lib/cloud9/EDES301/MiniDrum/projects"):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def get_project_list(self):
        """Returns a list of project names (without .json extension)."""
        files = os.listdir(self.directory)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]

    def save(self, name, grid_data, bpm):
        """Saves the grid and BPM to a JSON file."""
        filepath = os.path.join(self.directory, f"{name}.json")
        data = {
            "bpm": bpm,
            "grid": grid_data
        }
        with open(filepath, "w") as f:
            json.dump(data, f)
        print(f"Saved: {filepath}")

    def load(self, name):
        """Loads a project and returns (grid_data, bpm)."""
        filepath = os.path.join(self.directory, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                return data["grid"], data["bpm"]
        return None, None

    def delete(self, name):
        """Deletes a project file."""
        filepath = os.path.join(self.directory, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)