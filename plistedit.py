from plistlib import *
import os
def add_utf_info():
    print("Patching UTF-8 Support")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir=os.path.join(current_dir,"dist","Converter.app","Contents")
    plist_name="Info.plist"
    utf={'LSEnvironment': {'LANG': 'en_US.UTF-8', 'LC_ALL': 'en_US.UTF-8'}}
    with open (os.path.join(output_dir,plist_name),"rb") as f:
        plist:dict=load(f)
    plist.update(utf)
    with open (os.path.join(output_dir,plist_name),"wb") as f:
        dump(plist,f)
