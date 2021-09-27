import os

_basepath = os.path.dirname(__file__)

from .tfdetector import TFDetector
COCO = os.path.join(_basepath, "coco") 
BIRDFEEDER = os.path.join(_basepath, "birdfeeder") 