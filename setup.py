#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

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
    package_data = {"": ['*.so', '*.sign', '*.json'], "kritter": ["kvideocomp/*", "assets/*", "media/*", "kterm/*", "kterm/static/*", "keditor/*", "keditor/static/*", "login/*", "tflite/*"]},
    zip_safe=False    
    )