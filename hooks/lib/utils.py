import os
from pathlib import Path
import getpass


class TargetDir:
    def __init__(self, path=""):
        self.path = path

    def getPath(self, launchedFromRepo=False) -> Path:
        if launchedFromRepo:
            print("This script isn't being run directly.")
            ret = Path(os.path.dirname(Path(__file__).resolve()))
        else:
            print("This script is being run directly.")
            ret = Path(self.path)
        return ret


class dirManager:
    def __init__(self, path, isLaunchedFromRepo=False):
        self.isLaunchedFromRepo = isLaunchedFromRepo
        self.path = path
        self.execDir = self.execDir = Path(os.path.dirname(os.path.abspath(__file__)))

    def getTargetDir(self):
        return Path(self.path)

    def getExecDir(self):
        return self.execDir

    def getQuadletDir(self):
        path = Path(f"/home/{getpass.getuser()}/.config/containers/systemd")
        if getpass.getuser() == "root":
            path = Path(f"/etc/containers/systemd")
        return path

    def getSystemdDir(self):
        path = Path(f"/home/{getpass.getuser()}/.config/systemd/user")
        if getpass.getuser() == "root":
            path = Path(f"/usr/local/lib/systemd/system/")
        return path