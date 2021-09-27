from setuptools import setup
import os

about = {}
with open(os.path.join("src/kritter", "about.py"), encoding="utf-8") as fp:
    exec(fp.read(), about)

#depencencies
#quart
#termcolor
#dash
#dash-devices

setup(
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__email__'], 
    license=about['__license__'],
    package_dir={"": "src"},
    packages=["kritter"],
    package_data = {"": ['*.so', '*.sign'], "kritter": ["kvideocomp/*", "assets/*", "media/*", "kterm/*", "kterm/static/*", "keditor/*", "keditor/static/*", "login/*", "tf/*", "tf/coco/*", "tf/birdfeeder/*", "tflite/*", "tflite/coco/*"]},
    zip_safe=False    
    )