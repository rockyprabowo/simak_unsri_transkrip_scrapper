import os
import platform
from os.path import pathsep
from dotenv import load_dotenv
from pathlib import Path

defaults_path = Path('.') / 'defaults.txt'
dotenv_default_path = Path('.') / '.env'
dotenv_path = dotenv_default_path if os.path.isfile(
    dotenv_default_path) else defaults_path
load_dotenv(dotenv_path=dotenv_path)
__platform = platform.system()


class NoFirefoxFoundException(Exception):
    pass


def list_executables():
    global __platform
    paths = (Path(x)
             for x in os.environ["PATH"].split(pathsep) if Path(x).exists())
    executables = []
    pathexts = tuple(os.environ["PATHEXT"].lower().replace(
        ".", "").split(pathsep)) if __platform is "Windows" else ()

    def is_exec(_path, _file): return os.access(
        _path/_file, os.X_OK) and True if __platform is not "Windows" else _file.suffix.lower().endswith(pathexts)

    for path in [_path for _path in paths if _path.is_dir()]:
        for _executables in [_file for _file in path.iterdir() if is_exec(path, _file)]:
            executables.append(str(_executables))

    return executables


def try_obtain_firefox_binary():
    sub = "firefox"
    executables = list_executables()
    search_results = [s for s in executables if sub in s]
    if search_results:
        return search_results[0]
    else:
        raise NoFirefoxFoundException()


default_nim = os.getenv("DEFAULT_NIM")
default_password = os.getenv("DEFAULT_PASSWORD")
default_fakultas = os.getenv("DEFAULT_FAKULTAS")
default_prodi = os.getenv("DEFAULT_PRODI")
webdriver_headless = True if os.getenv(
    "WEBDRIVER_HEADLESS") == "true" else False
try:
    default_firefox_binary_path = os.getenv(
        "DEFAULT_FIREFOX_BINARY_PATH") or try_obtain_firefox_binary()
except NoFirefoxFoundException:
    print(
        f"Tidak dapat menentukan letak file biner Firefox. Silakan tambahkan letak file biner Firefox di bagian \"DEFAULT_FIREFOX_BINARY_PATH\" pada file {defaults_path}")
    exit(1)

print("JSON Dumper Transkrip Nilai SIMAK Universitas Sriwijaya")
print(f"Menggunakan opsi dari file {dotenv_path}")
print("Here we go...")
