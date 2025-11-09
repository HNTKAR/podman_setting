import os
import subprocess
import configparser
from pathlib import Path
from lib.utils import dirManager
import shutil


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

    def reload(self):
        print("Reloading systemd user daemon...")
        subprocess.run(["systemctl", "--user", "daemon-reload"])

    def startPod(self, podName):
        print(f"Starting pod: {podName}...")
        subprocess.run(["systemctl", "--user", "restart", podName])

    def startContainer(self, containerName):
        print(f"Starting container: {containerName}...")
        subprocess.run(["systemctl", "--user", "restart", containerName])

    def startBuild(self, buildName):
        print(f"Starting build: {buildName}...")
        subprocess.run(["systemctl", "--user", "restart", buildName])

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


class setup:
    def __init__(self, dir: Path, launchedFromRepo: bool):
        self.dir = dir
        self.launchedFromRepo = launchedFromRepo

    def copyQuadletFile(self, systemd: sysemctlCommand,appendPath:Path):
        print("This is the hook for pod.")

        dManager = dirManager(self.dir, self.launchedFromRepo)
        path = dManager.getTargetDir()
        print(f"path -> {path}")
        quadletFile_path = list(Path(path).rglob("Quadlet/*"))
        for i in quadletFile_path:
            print(f"copy {i.name} to {dManager.getQuadletDir()}")
            shutil.copyfile(i.resolve(), f"{dManager.getQuadletDir()}/{i.name}")

            # systemdに登録
            f = unitFile(Path(f"{dManager.getQuadletDir()}/{i.name}"))
            if f.getExt() == "build":
                f.changeWorkingDirectoryInBuildService(path)
            print(f"test {appendPath.absolute()}/Quadlet/{i.name}")
            f.appendPersonalChanges(f"{appendPath.absolute()}/Quadlet/{i.name}")
            systemd.setService(f.ext, f.serviceType)
