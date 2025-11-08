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

    def setService(self, serviceType, name):
        if serviceType == "container":
            self.containers.append(name)
        elif serviceType == "pod":
            self.pods.append(name)
        elif serviceType == "kube":
            self.kubes.append(name)
        elif serviceType == "network":
            self.networks.append(name)
        elif serviceType == "volume":
            self.volumes.append(name)
        elif serviceType == "build":
            self.builds.append(name)
        elif serviceType == "image":
            self.images.append(name)
        elif serviceType == "artifact":
            self.artifacts.append(name)
        else:
            self.unknowns.append(name)
            print(f"unknown service type: {name}")

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

    def startAllPod(self):
        for podName in self.pods:
            self.startPod(podName)

    def startAllContainer(self):
        for containerName in self.containers:
            self.startContainer(containerName)

    def startAllBuild(self):
        for buildName in self.builds:
            self.startBuild(buildName)


def mainProcess(dir, systemd, launchedFromRepo):
    """個人向け設定反映用プログラム

    Args:
        dir (_type_): ディレクトリパス
        launchedFromRepo (bool): repo経由か否かを判別
    """
    print("This is the hook for file pod.")
    cf = configparser.ConfigParser(strict=False)
    td = TargetDir(dir)
    p = td.getPath(launchedFromRepo)
    pod_path = list(Path(p).rglob("Quadlet/*"))
    for i in pod_path:
        print(f"copy {i.name} to {SYSTEMD_DIR}")
        shutil.copyfile(i.resolve(), f"{SYSTEMD_DIR}/{i.name}")
        # 拡張子を取得
        type = os.path.splitext(i.name)[-1][1:]
        print(f"file is {SYSTEMD_DIR}/{i.name}")
        cf.read(f"{SYSTEMD_DIR}/{i.name}")

        # systemdに登録
        systemd.setService(type, cf.get(type.capitalize(), "ServiceName"))


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
    si.startAllPod()


if __name__ == "__main__":
    print(f"main ok->{sys.argv[1]}")
    si = systemdInstance()
    mainProcess(sys.argv[1], si, False)
    si.reload()
    si.startAllPod()
