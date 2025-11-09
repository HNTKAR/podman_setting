#!/usr/bin/env python
from pathlib import Path
import sys
from lib.systemd import sysemctlCommand
from lib.systemd import setup
import argparse


def main(args):
    si = sysemctlCommand()
    repoPath:Path=args.repoPath
    appendPath:Path=args.appendPath
    commands:str=args.systemctl
    s = setup(repoPath, False)
    s.copyQuadletFile(si,appendPath=appendPath)
    si.reload()
    print(f"command is {commands}")
    for i in commands:
        match i:
            case "b":
                si.startAllBuilds()
            case "p":
                si.startAllPods()
            case "c":
                si.startAllContainers()


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repoPath",type=Path,help="Unitファイルがある場所",required=True)
    parser.add_argument("--appendPath",type=Path,help="Unitファイルの追記ファイルがあるディレクトリ",required=True)
    parser.add_argument("--systemctl",type=str,help="systemctlを使用した操作",default="")
    args=parser.parse_args()
    
    main(args)
