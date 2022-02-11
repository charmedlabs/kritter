#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os

_basepath = os.path.dirname(__file__)

from .tfdetector import TFDetector
COCO = os.path.join(_basepath, "coco") 
BIRDFEEDER = os.path.join(_basepath, "birdfeeder") 