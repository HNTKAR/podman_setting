#!/usr/bin/env python
from pathlib import Path
import os, sys, getpass, shutil

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


def mainProcess(dir, launchedFromRepo):
    """個人向け設定反映用プログラム

    Args:
        dir (_type_): ディレクトリパス
        launchedFromRepo (bool): repo経由か否かを判別
    """
    print("This is the hook for file pod.")
    td = TargetDir(dir)
    p = td.getPath(launchedFromRepo)
    pod_path = list(Path(p).rglob("Quadlet/*"))
    for i in pod_path:
        shutil.copyfile(i.resolve(), f"{SYSTEMD_DIR}/{i.name}")
        print(f"copy {i.name} to {SYSTEMD_DIR}")


def main(repo_topdir=None, **kwargs):
    """Main function invoked directly by repo.

    We must use the name "main" as that is what repo requires.

    Args:
      repo_topdir: The absolute path to the top-level directory of the repo workspace.
      kwargs: Leave this here for forward-compatibility.
    """
    print(f"Post-sync hook executed in repo at {repo_topdir}")
    mainProcess(repo_topdir, True)


if __name__ == "__main__":
    print(f"main ok->{sys.argv[1]}")
    mainProcess(sys.argv[1], False)
