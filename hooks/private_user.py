#!/usr/bin/env python
import os
import subprocess
import getpass
import shutil
import sys


def main(repo_topdir=None, **kwargs):
    """Main function invoked directly by repo.

    We must use the name "main" as that is what repo requires.

    Args:
      repo_topdir: The absolute path to the top-level directory of the repo workspace.
      kwargs: Leave this here for forward-compatibility.
    """

    print(f"Post-sync hook executed in repo at {repo_topdir}")
    print("This is the podman_setting post-sync hook.")

    print(f"user name is {getpass.getuser()}")
    if not repo_topdir:
        print("repo_topdir is None, exiting.")
        return

    HookDir = os.path.join(repo_topdir, "setup", "podman", "hooks")
    PodmanDir = os.path.join(repo_topdir, "setup", "podman", "podman")

    os.chdir(HookDir)
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{HookDir}:{env.get("PYTHONPATH", "")}"

    # copy multiple files for file-pod

    dir = "file"
    containers = ["samba", "nginx"]
    filename_lists = [
        ["smb-include.conf"],
        # ["h-sample_3birds_uk.conf", "s-test.conf"],
        [],
    ]
    for container, filenames in zip(containers, filename_lists):
        copy_for_pod(filenames, dir, container, repo_topdir, PodmanDir)

    subprocess.run(
        [
            "python3",
            f"{HookDir}/applyChange.py",
            f"--repoPath",
            f"{repo_topdir}/podman/{dir}",
            f"--appendPath",
            f"{PodmanDir}/{dir}",
            f"--delete-param-from-quadlet",
            f"pod",
            f"8080",
            f"--systemctl",
            f"bp",
        ],
        env=env,
    )

    # copy multiple files for certbot

    dir = "certbot"
    filenames = []
    copy_for_container(filenames, dir, repo_topdir, PodmanDir)
    subprocess.run(
        [
            "python3",
            f"{HookDir}/applyChange.py",
            f"--repoPath",
            f"{repo_topdir}/podman/{dir}",
            f"--appendPath",
            f"{PodmanDir}/{dir}",
            f"--systemctl",
            f"bc",
        ],
        env=env,
    )


def copy_for_pod(filenames, dir, container, repo_topdir, PodmanDir):
    """
    指定されたPod用の設定ファイルをコピーします。
    Args:
        filenames: コピーするファイル名のリスト。
        dir: ファイルが存在するディレクトリ。
        container: コンテナ名。
        repo_topdir: リポジトリ作業領域のトップレベルディレクトリへの絶対パス。
        PodmanDir: podman構成の基底ディレクトリ。
    """
    for filename in filenames:
        shutil.copyfile(
            f"{PodmanDir}/{dir}/{filename}",
            f"{repo_topdir}/podman/{dir}/{container}/config/{filename}",
        )


def copy_for_container(filenames, dir, repo_topdir, PodmanDir):
    """
    指定されたコンテナ用の設定ファイルをコピーします。
    Args:
      filenames: コピーするファイル名のリスト。
      dir: ファイルが存在するディレクトリ。
      repo_topdir: リポジトリ作業領域のトップレベルディレクトリへの絶対パス。
      PodmanDir: podman構成の基底ディレクトリ。
    """
    for filename in filenames:
        shutil.copyfile(
            f"{PodmanDir}/{dir}/{filename}",
            f"{repo_topdir}/podman/{dir}/config/{filename}",
        )


if __name__ == "__main__":
    main(sys.argv[1])
