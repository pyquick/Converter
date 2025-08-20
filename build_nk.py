import subprocess,shutil

try:
    shutil.rmtree("build")
except :
    pass
try:
    shutil.rmtree("dist")
except:
    pass
subprocess.run("./build_nk.command",shell=True,capture_output=True,text=True,stdout=True)
import patch