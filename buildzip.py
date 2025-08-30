from support.convertzip import create_zip
def build_zip():
    print("Building Zip")
    create_zip("./dist/Converter.zip",["./dist/Converter.app"])