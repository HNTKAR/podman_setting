#!/usr/bin/env python
from pathlib import Path
from lib.setup import setup
import argparse


def main(args):
    repoPath: Path = args.repoPath
    appendPath: Path = args.appendPath
    commands: str = args.systemctl
    s = setup(repoPath, False)
    s.setupQuadletFiles(appendPath)
    s.setupSystemdFiles(appendPath)
    s.reload()
    print(f"command is {commands}")
    for i in commands:
        match i:
            case "b":
                s.startAllBuilds()
            case "p":
                s.startAllPods()
            case "c":
                s.startAllContainers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repoPath", type=Path, help="Unitファイルがある場所", required=True
    )
    parser.add_argument(
        "--appendPath",
        type=Path,
        help="Unitファイルの追記ファイルがあるディレクトリ",
        required=True,
    )
    parser.add_argument(
        "--systemctl", type=str, help="systemctlを使用した操作", default=""
    )
    args = parser.parse_args()

    main(args)
