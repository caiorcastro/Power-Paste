from setuptools import setup

APP = ["power_paste.py"]
DATA_FILES = ["icon.png"]
OPTIONS = {
    "packages": ["rumps", "PIL", "pyperclip"],
    "includes": ["rumps", "pyperclip", "PIL", "Foundation", "AppKit", "objc"],
    "iconfile": "icon.png",
    "plist": {
        "CFBundleName": "Power Paste",
        "CFBundleDisplayName": "Power Paste",
        "CFBundleGetInfoString": "Gerenciador de área de transferência para macOS",
        "CFBundleIdentifier": "com.caiorcastro.powerpaste",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright": "Copyright © 2024 Caio Castro",
        "LSUIElement": 1,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)