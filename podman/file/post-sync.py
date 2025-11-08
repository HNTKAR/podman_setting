#!/usr/bin/env python
from pathlib import Path
import getpass, os, shutil, subprocess, sys
import configparser

SYSTEMD_DIR = f"/home/{getpass.getuser()}/.config/containers/systemd"


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


class serviceFile:
    def __init__(self, path="", workDir=""):
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

    def applyChanges(self, appendFile):
        if not os.path.exists(appendFile):
            print(f"append file {appendFile} not found, skipping...")
            return
        with open(self.path, "a") as ServiceFile:
            with open(appendFile, "r") as appendFile:
                ServiceFile.write(f"# Added by podman file post-sync hook\n")
                ServiceFile.write(f"\n")
                for line in appendFile:
                    ServiceFile.write(line)

    def changeWorkingDirectoryInBuildService(self, dirPath):
        with open(self.path, "a") as ServiceFile:
            ServiceFile.write(f"\n")
            ServiceFile.write(f"# Added by podman file post-sync hook\n")
            ServiceFile.write(f"[{self.ext.capitalize()}]\n")
            ServiceFile.write(f"SetWorkingDirectory={dirPath}\n")
        pass


class systemdInstance:
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


def mainProcess(dir, systemd, launchedFromRepo):
    """個人向け設定反映用プログラム

    Args:
        dir (_type_): ディレクトリパス
        launchedFromRepo (bool): repo経由か否かを判別
    """
    print("This is the hook for file pod.")

    td = TargetDir(dir)
    p = td.getPath(launchedFromRepo)
    quadletFile_path = list(Path(p).rglob("Quadlet/*"))
    for i in quadletFile_path:
        print(f"copy {i.name} to {SYSTEMD_DIR}")
        shutil.copyfile(i.resolve(), f"{SYSTEMD_DIR}/{i.name}")

        # systemdに登録
        file = serviceFile(f"{SYSTEMD_DIR}/{i.name}")
        if file.getExt() == "build":
            file.changeWorkingDirectoryInBuildService(p)
        file.applyChanges(f"{os.path.dirname(__file__)}/Quadlet/{i.name}")
        systemd.setService(file.ext, file.serviceType)


def main(repo_topdir=None, **kwargs):
    """Main function invoked directly by repo.

    We must use the name "main" as that is what repo requires.

    Args:
      repo_topdir: The absolute path to the top-level directory of the repo workspace.
      kwargs: Leave this here for forward-compatibility.
    """
    print(f"Post-sync hook executed in repo at {repo_topdir}")
    si = systemdInstance()
    mainProcess(repo_topdir, si, True)
    si.reload()
    si.startAllBuilds()
    si.startAllPods()


if __name__ == "__main__":
    print(f"main ok->{sys.argv[1]}")
    si = systemdInstance()
    mainProcess(sys.argv[1], si, False)
    si.reload()
    si.startAllBuilds()
    si.startAllPods()
