from build_nk import main
import clean
import buildzip
from setup_ccache import setup_ccache
from patch import _patch_load_command,_patch_sdk_version
if __name__ == "__main__":
    clean.clean()
    setup_ccache()
    main()
    _patch_load_command()
    _patch_sdk_version()
    buildzip.build_zip()