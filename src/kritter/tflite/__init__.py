import os

_basepath = os.path.dirname(__file__)

from .tflitedetector import TFliteDetector
COCO = os.path.join(_basepath, "coco") 
