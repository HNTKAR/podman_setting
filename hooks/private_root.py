#!/usr/bin/env python
import os
import subprocess
import getpass
import shutil


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

    HookRoot = os.path.join(repo_topdir, "setup", "podman", "hooks")

    os.chdir(HookRoot)
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{repo_topdir}/setup/podman/hooks:{env.get("PYTHONPATH", "")}"

    # copy multiple files for file-pod

    filenames = ["smb-include.conf"]
    for filename in filenames:
        shutil.copyfile(
            f"{HookRoot}/file/{filename}",
            f"{repo_topdir}/podman/file/samba/config/{filename}",
        )
    subprocess.run(
        [
            "python3",
            f"{HookRoot}/applyChange.py",
            f"{repo_topdir}/podman/file",
        ],
        env=env,
    )
