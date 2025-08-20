import subprocess,shutil

try:
    shutil.rmtree("build")
except :
    pass
try:
    shutil.rmtree("dist")
except:
    pass
print(subprocess.run("pyinstaller convert.spec",shell=True,capture_output=True,text=True))
import patch