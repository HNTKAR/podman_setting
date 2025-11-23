#!/usr/bin/env python
from pathlib import Path
from lib.setup import setup
import argparse


def main(args):
    repoPath: Path = args.repoPath
    appendPath: Path = args.appendPath
    commands: str = args.systemctl
    quadletDeleteParam: list[list[str]] = args.delete_param_from_quadlet
    systemdDeleteParam: list[list[str]] = args.delete_param_from_systemd
    s = setup(repoPath, False)
    s.setupQuadletFiles(appendPath, quadletDeleteParam)
    s.setupSystemdFiles(appendPath, systemdDeleteParam)
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
        "--repoPath", type=Path, help="podman用リポジトリのroot", required=True
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
    parser.add_argument(
        "--delete-param-from-quadlet",
        type=str,
        nargs=2,
        action="append",
        help="Quadletファイルから削除するパラメータ",
        default=[],
    )
    parser.add_argument(
        "--delete-param-from-systemd",
        type=str,
        action="append",
        help="systemdユニットファイルから削除するパラメータ",
        default=[],
    )
    args = parser.parse_args()

    main(args)
