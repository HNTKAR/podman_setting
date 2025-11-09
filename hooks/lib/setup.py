from pathlib import Path
from lib.utils import dirManager
from lib.systemd import sysemctlCommand, unitFile
import shutil


class setup(sysemctlCommand):
    def __init__(self, dir: Path, launchedFromRepo: bool):
        super().__init__()
        self.dir = dir
        self.launchedFromRepo = launchedFromRepo
        self.dManager = dirManager(dir, launchedFromRepo)

    def searchQuadletFiles(self):
        path = self.dManager.getTargetDir()
        return list(Path(path).rglob("Quadlet/*"))

    def searchSystemdFiles(self):
        path = self.dManager.getTargetDir()
        return list(Path(path).rglob("Systemd/*"))

    def modifySystemdFiles(self, sFiles: list[Path], appendPath: Path):
        for i in sFiles:
            # systemdに登録
            f = unitFile(Path(f"{self.dManager.getSystemdDir()}/{i.name}"))
            f.appendPersonalChanges(f"{appendPath.resolve()}/Systemd/{i.name}")

    def modifyQuadletFiles(self, qFiles: list[Path], appendPath: Path):
        for i in qFiles:
            # systemdに登録
            f = unitFile(Path(f"{self.dManager.getQuadletDir()}/{i.name}"))
            if f.getExt() == "build":
                f.changeWorkingDirectoryInBuildService(self.dManager.getTargetDir())
            f.appendPersonalChanges(f"{appendPath.resolve()}/Quadlet/{i.name}")

    def updateUnitFileLists(self, qFiles: list[Path]):
        for i in qFiles:
            f = unitFile(Path(f"{self.dManager.getQuadletDir()}/{i.name}"))
            self.setService(f.ext, f.serviceType)

    def copyQuadletFile(self, qFiles: list[Path]):
        for i in qFiles:
            # ファイルをコピー
            print(f"copy {i.name} to {self.dManager.getQuadletDir()}")
            shutil.copyfile(i.resolve(), f"{self.dManager.getQuadletDir()}/{i.name}")

    def copySystemdFile(self, sFiles: list[Path]):
        for i in sFiles:
            # ファイルをコピー
            print(f"copy {i.name} to {self.dManager.getSystemdDir()}")
            shutil.copyfile(i.resolve(), f"{self.dManager.getSystemdDir()}/{i.name}")

    def setupQuadletFiles(self, appendPath: Path):
        print("This is the hook for Quadlet.")
        quadletFiles = self.searchQuadletFiles()
        self.copyQuadletFile(quadletFiles)
        self.modifyQuadletFiles(quadletFiles, appendPath)
        self.updateUnitFileLists(quadletFiles)

    def setupSystemdFiles(self, appendPath: Path):
        print("This is the hook for systemd.")
        systemdFiles = self.searchSystemdFiles()
        self.copySystemdFile(systemdFiles)
        self.modifySystemdFiles(systemdFiles, appendPath)
