#!/usr/bin/env python
import os
import subprocess


def main(repo_topdir=None, **kwargs):
    """Main function invoked directly by repo.

    We must use the name "main" as that is what repo requires.

    Args:
      repo_topdir: The absolute path to the top-level directory of the repo workspace.
      kwargs: Leave this here for forward-compatibility.
    """

    print(f"Post-sync hook executed in repo at {repo_topdir}")
    print("This is the podman_setting post-sync hook.")

    path = os.path.dirname(__file__)
    subprocess.run(["python3", f"{path}/hooks/private_user.py", f"{repo_topdir}"])
    subprocess.run(["python3", f"{path}/hooks/private_root.py", f"{repo_topdir}"])
