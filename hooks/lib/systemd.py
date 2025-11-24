import os
import subprocess
import configparser
import getpass
from pathlib import Path
from collections import defaultdict


class sysemctlCommand:
    def __init__(self):
        self.quadlet_files = defaultdict(list)
        self.ext_lists = unitFile.quadlet_ext

    def setService(self, ext, serviceName):
        self.quadlet_files[ext].append(serviceName)
        if ext not in self.ext_lists:
            print(f"unknown extension: {ext} for service {serviceName}")

    def getCommand(self, command: list):
        prefix = ["systemctl"]
        if getpass.getuser() != "root":
            prefix += ["--user"]
        return prefix + command

    def reload(self):
        print("Reloading systemd user daemon...")
        subprocess.run(self.getCommand(["daemon-reload"]))

    def startPod(self, podName):
        print(f"Starting pod: {podName}...")
        subprocess.run(self.getCommand(["restart", podName]))

    def startContainer(self, containerName):
        print(f"Starting container: {containerName}...")
        subprocess.run(self.getCommand(["restart", containerName]))

    def startBuild(self, buildName):
        print(f"Starting build: {buildName}...")
        subprocess.run(self.getCommand(["restart", buildName]))

    def startAllPods(self):
        for podName in self.quadlet_files["pod"]:
            self.startPod(podName)

    def startAllContainers(self):
        for containerName in self.quadlet_files["container"]:
            self.startContainer(containerName)

    def startAllBuilds(self):
        for buildName in self.quadlet_files["build"]:
            self.startBuild(buildName)


class unitFile:
    quadlet_ext = [
        "container",
        "pod",
        "kube",
        "network",
        "volume",
        "build",
        "image",
        "artifact",
    ]

    def __init__(self, path: Path):

        self.path = path
        self.ext = os.path.splitext(self.path)[-1][1:]

    def getServiceType(self):
        cf = configparser.ConfigParser(strict=False)
        cf.read(self.path)
        ret=""
        if self.ext in self.quadlet_ext:
            ret= cf.get(self.ext.capitalize(), "ServiceName")
        return ret

    def getPath(self):
        return self.path

    def getExt(self):
        return self.ext

    def appendPersonalChanges(self, targetFile):
        with open(targetFile, "a") as ServiceFile:
            ServiceFile.write(f"\n")
            ServiceFile.write(f"# Added by podman file post-sync hook\n")
            with open(self.path, "r") as appendFile:
                for line in appendFile:
                    ServiceFile.write(line)

    def deleteDefaultParams(self, param: str):
        if not param:
            return
        print(f"Deleting param {param} from {self.path}")
        with open(self.path, "r") as ServiceFile:
            lines = ServiceFile.readlines()
        with open(self.path, "w") as ServiceFile:
            for line in lines:
                if param not in line:
                    ServiceFile.write(line)

    def changeWorkingDirectoryInBuildService(self, dirPath):
        with open(self.path, "a") as ServiceFile:
            ServiceFile.write(f"\n")
            ServiceFile.write(f"# Added by podman file post-sync hook\n")
            ServiceFile.write(f"[{self.ext.capitalize()}]\n")
            ServiceFile.write(f"SetWorkingDirectory={dirPath}\n")
