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
        """
        インスタンスの dManager が提供するターゲットディレクトリ配下にある
        すべての "Quadlet" サブディレクトリ直下のファイルおよびディレクトリを検索して返します。

        Returns:
            list[pathlib.Path]: 検索結果の pathlib.Path オブジェクトのリスト。
        """
        path = self.dManager.getTargetDir()
        return list(Path(path).rglob("Quadlet/*"))

    def searchSystemdFiles(self) -> list[Path]:
        """
        self.dManager が示すターゲットディレクトリ配下の
        "Systemd" サブディレクトリ直下にあるすべてのファイル・ディレクトリを検索して返します。

        Returns:
            list[pathlib.Path]: 検索結果の pathlib.Path オブジェクトのリスト（見つからない場合は空リスト）。
        """
        path = self.dManager.getTargetDir()
        return list(Path(path).rglob("Systemd/*"))

    def modifySystemdFiles(self, sFiles: list[Path], appendPath: Path):
        """
        systemdユニットファイルに対して、ユーザ/環境ごとの追記を行います。

        Args:
            sFiles (list[Path]): systemdディレクトリにあるユニットファイルを表すPathのリスト。
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Systemd/<unit> を参照します。
        """
        for i in sFiles:
            # systemdに登録
            f = unitFile(Path(f"{self.dManager.getSystemdDir()}/{i.name}"))
            f.appendPersonalChanges(f"{appendPath.resolve()}/Systemd/{i.name}")

    def modifyQuadletFiles(self, qFiles: list[Path], appendPath: Path):
        """
        Quadletユニットファイルに対して、ユーザ/環境ごとの追記を行います。
        Returns:
            qFiles (list[Path]): Quadletディレクトリにあるユニットファイルを表すPathのリスト。
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Quadlet/<unit> を参照します。
        """
        for i in qFiles:
            # systemdに登録
            f = unitFile(Path(f"{self.dManager.getQuadletDir()}/{i.name}"))
            if f.getExt() == "build":
                f.changeWorkingDirectoryInBuildService(self.dManager.getTargetDir())
            f.appendPersonalChanges(f"{appendPath.resolve()}/Quadlet/{i.name}")

    def updateUnitFileLists(self, qFiles: list[Path]):
        """
        Quadletユニットファイルのリストを更新します。
        Returns:
            qFiles (list[Path]): Quadletディレクトリにあるユニットファイルを表すPathのリスト。
        """
        for i in qFiles:
            f = unitFile(Path(f"{self.dManager.getQuadletDir()}/{i.name}"))
            self.setService(f.ext, f.serviceType)

    def copyQuadletFile(self, qFiles: list[Path]):
        """
        Quadletユニットファイルをコピーします。
        Returns:
            qFiles (list[Path]): Quadletディレクトリにあるユニットファイルを表すPathのリスト。
        """
        for i in qFiles:
            # ファイルをコピー
            print(f"copy {i.name} to {self.dManager.getQuadletDir()}")
            shutil.copyfile(i.resolve(), f"{self.dManager.getQuadletDir()}/{i.name}")

    def copySystemdFile(self, sFiles: list[Path]):
        """
        systemdユニットファイルをコピーします。
        Returns:
            sFiles (list[Path]): systemdディレクトリにあるユニットファイルを表すPathのリスト。
        """
        for i in sFiles:
            # ファイルをコピー
            print(f"copy {i.name} to {self.dManager.getSystemdDir()}")
            shutil.copyfile(i.resolve(), f"{self.dManager.getSystemdDir()}/{i.name}")

    def setupQuadletFiles(self, appendPath: Path):
        """
        Quadletユニットファイルのセットアップを行います。
        Returns:
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Quadlet/<unit> を参照します。
        """
        print("This is the hook for Quadlet.")
        quadletFiles = self.searchQuadletFiles()
        self.copyQuadletFile(quadletFiles)
        self.modifyQuadletFiles(quadletFiles, appendPath)
        self.updateUnitFileLists(quadletFiles)

    def setupSystemdFiles(self, appendPath: Path):
        """
        systemdユニットファイルのセットアップを行います。
        Returns:
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Systemd/<unit> を参照します。
        """
        print("This is the hook for systemd.")
        systemdFiles = self.searchSystemdFiles()
        self.copySystemdFile(systemdFiles)
        self.modifySystemdFiles(systemdFiles, appendPath)
