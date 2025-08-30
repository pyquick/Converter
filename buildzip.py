from support.convertzip import create_zip
def build_zip():
    print("Building Zip")
    create_zip("./dist/Converter_arm64_darwin.zip",["./dist/Converter.app"])
def build_zip_intel():
    print("Building Zip")
    create_zip("./dist/Converter_intel.zip",["./dist/Converter.app"])