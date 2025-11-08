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
    
    PODMAN_HOOK_ROOT = repo_topdir + "/setting/podman"
    HOOK_FILENAME = {"post-sync": "post-sync.py", "None": "None"}
    os.chdir(PODMAN_HOOK_ROOT)
    
    # copy multiple files for file-pod 

    filenames = ["smb-include.conf"]
    for filename in filenames:
        shutil.copyfile(
            f"{PODMAN_HOOK_ROOT}/file/{filename}",
            f"{repo_topdir}/podman/file/samba/config/{filename}",
        )
    subprocess.run(
        [
            "python3",
            PODMAN_HOOK_ROOT + "/file/" + HOOK_FILENAME["post-sync"],
            f"{repo_topdir}/podman/file",
        ]
    )
