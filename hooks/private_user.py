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
    container = "samba"
    filenames = ["smb-include.conf"]
    for filename in filenames:
        shutil.copyfile(
            f"{PodmanDir}/{dir}/{filename}",
            f"{repo_topdir}/podman/{dir}/{container}/config/{filename}",
        )
    subprocess.run(
        [
            "python3",
            f"{HookDir}/applyChange.py",
            f"--repoPath",
            f"{repo_topdir}/podman/{dir}",
            f"--appendPath",
            f"{PodmanDir}/{dir}",
            f"--systemctl",
            f"bp",
        ],
        env=env,
    )
    # container = "nginx"
    # filenames = ["h-sample_3birds_uk.conf","s-test.conf"]
    # for filename in filenames:
    #     shutil.copyfile(
    #         f"{PodmanDir}/{dir}/{filename}",
    #         f"{repo_topdir}/podman/{dir}/{container}/config/{filename}",
    #     )
    # subprocess.run(
    #     [
    #         "python3",
    #         f"{HookDir}/applyChange.py",
    #         f"--repoPath",
    #         f"{repo_topdir}/podman/{dir}",
    #         f"--appendPath",
    #         f"{PodmanDir}/{dir}",
    #         f"--systemctl",
    #         f"bp",
    #     ],
    #     env=env,
    # )

    # copy multiple files for certbot

    dir = "certbot"
    filenames = []
    for filename in filenames:
        shutil.copyfile(
            f"{PodmanDir}/{dir}/{filename}",
            f"{repo_topdir}/podman/{dir}/config/{filename}",
        )
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
    
if __name__ == "__main__":
    main(sys.argv[1])
