def _patch_sdk_version() -> None:
        """
        Patch LC_BUILD_VERSION in Load Command to report the macOS 26 SDK

        This will enable the Solarium refresh when running on macOS 26
        Minor visual anomalies and padding issues exist, disable if not addressed before release
        """
        _application_output="./dist/Converter.app"
        _file = _application_output + "/Contents" + "/MacOS" + "/launcher"

        _find    = b'\x00\x01\x0C\x00'
        _replace = b'\x00\x00\x1A\x00'
        print("Patching LC_BUILD_VERSION")
        with open(_file, "rb") as f:
            data = f.read()
            data = data.replace(_find, _replace)

        with open(_file, "wb") as f:
            f.write(data)
def _patch_load_command():
        """
        Patch LC_VERSION_MIN_MACOSX in Load Command to report 10.10

        By default Pyinstaller will create binaries supporting 10.13+
        However this limitation is entirely arbitrary for our libraries
        and instead we're able to support 10.10 without issues.

        To verify set version:
          otool -l ./dist/OCLP-R.app/Contents/MacOS/OCLP-R

              cmd LC_VERSION_MIN_MACOSX
          cmdsize 16
          version 10.13
              sdk 10.9
        """
        _application_output="./dist/Converter.app"
        _file = _application_output + "/Contents" + "/MacOS" + "/launcher"

        _find    = b'\x00\x0D\x0A\x00'
        _replace = b'\x00\x0A\x0A\x00' # 10.10 (0xA0A)

        print("Patching LC_VERSION_MIN_MACOSX")
        with open(_file, "rb") as f:
            data = f.read()
            data = data.replace(_find, _replace, 1)

        with open(_file, "wb") as f:
            f.write(data)
