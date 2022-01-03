import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="HubblePi",
    version="2.0.0",
    author="Ronald Schreiber",
    description="Turns a Raspeberry Pi camera in a remote controlled camera for astrophotography.",
    license="MIT",
    keywords="RaspberryPi astrophotography",
    url="https://github.com/scriptorron/hubblepi",
    packages=find_packages(include=['HubblePi', 'HubblePi.*']),
    long_description=read('README.md'),
    install_requires=[
        "numpy",
        "rawpy==0.17.0",
        # We need PyQt5. But the conda package has a different name "pyqt". That makes the requirements
        # incompatible between conda and pip installations.
        #"PyQt5",
        "pillow",
        "pyqtgraph",
        "astropy",
        "colour-demosaicing==0.1.6",
        "pandas",
        "send2trash",
        "imageio"
    ],
    entry_points={
        'console_scripts': [
            'HubblePi_Capture=HubblePi.capture.HubblePi_Capture:main',
            'HubblePi_Viewer=HubblePi.viewer.HubblePi_Viewer:main',
            'HubblePi_RPi2Fits=HubblePi.tools.RPi2Fits:main',
        ]
    },
    data_files=[
        ('HubblePi/capture/presets', ['*.set']),
    ],
)