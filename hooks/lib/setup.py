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
        self.quadletDeleteParams = []
        self.systemdDeleteParams = []

    def searchQuadletFiles(self):
        """
        podman用リポジトリ配下にある "Quadlet" サブディレクトリ直下の
        ファイルおよびディレクトリを検索して返します。

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
        for sFile in sFiles:
            # systemdに登録
            f = unitFile(sFile)
            f.appendPersonalChanges(appendPath.resolve() / "Systemd" / sFile.name)

    def modifyQuadletFiles(self, qFiles: list[Path], appendPath: Path):
        """
        Quadletユニットファイルに対して、ユーザ/環境ごとの追記を行います。
        Returns:
            qFiles (list[Path]): Quadletディレクトリにあるユニットファイルを表すPathのリスト。
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Quadlet/<unit> を参照します。
        """
        for qFile in qFiles:
            f = unitFile(qFile)
            if f.getExt() == "build":
                f.changeWorkingDirectoryInBuildService(self.dManager.getTargetDir())
            f.appendPersonalChanges(appendPath.resolve() / "Quadlet" / qFile.name)

    def updateUnitFileLists(self, qFiles: list[Path]):
        """
        Quadletユニットファイルのリストを更新します。
        Returns:
            qFiles (list[Path]): Quadletディレクトリにあるユニットファイルを表すPathのリスト。
        """
        for qFile in qFiles:
            f = unitFile(qFile)
            self.setService(f.ext, f.serviceType)

    def copyQuadletFile(self, qFiles: list[Path], copiedFiles: list[Path]):
        """
        Quadletユニットファイルをコピーします。
        Returns:
            qFiles (list[Path]): Quadletディレクトリにあるユニットファイルを表すPathのリスト。
        """
        for i in qFiles:
            # ファイルをコピー
            print(f"copy {i.name} to {self.dManager.getQuadletDir()}")
            copyFile = f"{self.dManager.getQuadletDir()}/{i.name}"
            shutil.copyfile(i.resolve(), copyFile)
            copiedFiles.append(Path(copyFile))

    def copySystemdFile(self, sFiles: list[Path], copiedFiles: list[Path]):
        """
        systemdユニットファイルをコピーします。
        Returns:
            sFiles (list[Path]): systemdディレクトリにあるユニットファイルを表すPathのリスト。
        """
        for i in sFiles:
            # ファイルをコピー
            print(f"copy {i.name} to {self.dManager.getSystemdDir()}")
            copyFile = f"{self.dManager.getSystemdDir()}/{i.name}"
            shutil.copyfile(i.resolve(), copyFile)
            copiedFiles.append(Path(copyFile))

    def setupQuadletFiles(
        self, appendPath: Path, deleteParamsFromQuadlet: list[list[str]]
    ):
        """
        Quadletユニットファイルのセットアップを行います。
        Returns:
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Quadlet/<unit> を参照します。
        """
        print("This is the hook for Quadlet.")
        quadletFiles = self.searchQuadletFiles()
        copiedFiles: list[Path] = []
        self.copyQuadletFile(quadletFiles, copiedFiles)
        self.updateUnitFileLists(copiedFiles)
        self.modifyQuadletFiles(copiedFiles, appendPath)
        self.deleteDefalutParams(copiedFiles, deleteParamsFromQuadlet)

    def setupSystemdFiles(
        self, appendPath: Path, deleteParamsFromSystemd: list[list[str]]
    ):
        """
        systemdユニットファイルのセットアップを行います。
        Returns:
            appendPath (Path): 追記元ファイルが格納されたベースパス。<appendPath>/Systemd/<unit> を参照します。
        """
        print("This is the hook for systemd.")
        systemdFiles = self.searchSystemdFiles()
        copiedFiles: list[Path] = []
        self.copySystemdFile(systemdFiles, copiedFiles)
        self.modifySystemdFiles(copiedFiles, appendPath)
        self.deleteDefalutParams(copiedFiles, deleteParamsFromSystemd)

    def deleteDefalutParams(
        self, qFiles, deleteParams: list[list[str]]
    ):
        """
        ユニットファイルから指定されたパラメータを削除します。
        Args:
            deleteParams (list[list[str]]): 削除するパラメータのリスト。各要素は [カンマ区切りの拡張子, 削除したい文字列] の形式です。
        """
        for exts, deleteContext in deleteParams:
            ext_list = []
            if "," in exts:
                ext_list = exts.split(",")
            else:
                ext_list = [exts]
            for ext in ext_list:
                for qFile in qFiles:
                    f = unitFile(qFile)
                    if f.getExt() == ext:
                        f.deleteDefaultParams(deleteContext)
