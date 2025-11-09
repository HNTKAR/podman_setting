import os
import subprocess
import configparser
import getpass
from pathlib import Path


class sysemctlCommand:
    def __init__(self):
        self.containers = []
        self.pods = []
        self.kubes = []
        self.networks = []
        self.volumes = []
        self.builds = []
        self.images = []
        self.artifacts = []
        self.unknowns = []

    def setService(self, ext, serviceName):
        if ext == "container":
            self.containers.append(serviceName)
        elif ext == "pod":
            self.pods.append(serviceName)
        elif ext == "kube":
            self.kubes.append(serviceName)
        elif ext == "network":
            self.networks.append(serviceName)
        elif ext == "volume":
            self.volumes.append(serviceName)
        elif ext == "build":
            self.builds.append(serviceName)
        elif ext == "image":
            self.images.append(serviceName)
        elif ext == "artifact":
            self.artifacts.append(serviceName)
        else:
            self.unknowns.append(serviceName)
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
        for podName in self.pods:
            self.startPod(podName)

    def startAllContainers(self):
        for containerName in self.containers:
            self.startContainer(containerName)

    def startAllBuilds(self):
        for buildName in self.builds:
            self.startBuild(buildName)


class unitFile:
    def __init__(self, path: Path):
        cf = configparser.ConfigParser(strict=False)
        cf.read(path)

        self.path = path
        self.ext = os.path.splitext(self.path)[-1][1:]
        self.serviceType = cf.get(self.ext.capitalize(), "ServiceName")

    def getServiceType(self):
        return self.serviceType

    def getPath(self):
        return self.path

    def getExt(self):
        return self.ext

    def appendPersonalChanges(self, appendFile):
        if not os.path.exists(appendFile):
            print(f"append file {appendFile} not found, skipping...")
            return
        with open(self.path, "a") as ServiceFile:
            ServiceFile.write(f"\n")
            ServiceFile.write(f"# Added by podman file post-sync hook\n")
            with open(appendFile, "r") as appendFile:
                for line in appendFile:
                    ServiceFile.write(line)

    def changeWorkingDirectoryInBuildService(self, dirPath):
        with open(self.path, "a") as ServiceFile:
            ServiceFile.write(f"\n")
            ServiceFile.write(f"# Added by podman file post-sync hook\n")
            ServiceFile.write(f"[{self.ext.capitalize()}]\n")
            ServiceFile.write(f"SetWorkingDirectory={dirPath}\n")
