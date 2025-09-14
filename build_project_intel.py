from build_nk import main
import clean
import buildzip
from setup_ccache import setup_ccache
from patch import _patch_load_command,_patch_sdk_version
from plistedit import add_utf_info
if __name__ == "__main__":
    clean.clean()
    setup_ccache()
    main()
    _patch_load_command()
    _patch_sdk_version()
    add_utf_info()
    buildzip.build_zip_intel()