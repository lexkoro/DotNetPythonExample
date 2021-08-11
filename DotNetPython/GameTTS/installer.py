import subprocess
import pkg_resources
from pathlib import Path

required = {
"pydub",
"pysbd",
"numpy",
"scipy",
"librosa",
"unidecode",
"gruut",
"gruut[de]",
"torch"}

installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

APP_FOLDER = Path(Path(__name__).parent.resolve())

def install_deps():
    try:
        python = Path(APP_FOLDER, "PythonRuntime", "python.exe")
        subprocess.check_call([python, '-m', 'pip', 'install', *missing, '--no-warn-script-location'], stdout=subprocess.DEVNULL)
        return 0
    except Exception as err:
        print(err)
        return 1

def validate_deps():
    try:
        fixed_missing = missing.copy()
        fixed_missing.remove("gruut[de]")
        if fixed_missing:
            print("install missing deps")
            return install_deps()
        else:
            print("all deps installed")
            return 0
    except Exception as err:
        print(err)
        return 1