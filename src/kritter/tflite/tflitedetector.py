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
from pydoc import importfile
from kritter import KimageDetector
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import cv2

BASEDIR = os.path.dirname(__file__)

class TFliteDetector(KimageDetector):
    def __init__(self, model=None, threshold=0.75):
        super().__init__()
        # If model isn't specified, use the common objects network
        if not model:
            model = os.path.join(BASEDIR, "efficientdet_lite0.tflite")
        self.get_consts(model)
        self.threshold = threshold
        base_options = core.BaseOptions(file_name=model, use_coral=False, num_threads=4)
        detection_options = processor.DetectionOptions(score_threshold=0.1)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        self.detector = vision.ObjectDetector.create_from_options(options)

    def foo(self):
        print("foo")

    def detect(self, image, threshold=None):
        if not threshold:
            threshold = self.threshold
        res = []
        orig_resolution = (image.shape[1], image.shape[0])
        new_resolution = (640, 480)
        scale = (orig_resolution[0]/new_resolution[0], orig_resolution[1]/new_resolution[1])
        image = cv2.resize(image, new_resolution)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_tensor = vision.TensorImage.create_from_array(image)
        # Run object detection estimation using the model.
        detected = self.detector.detect(input_tensor)
        for d in detected.detections:
            scores = [c.score for c in d.classes]
            max_score = max(scores)
            if max_score<threshold:
                continue
            max_index = scores.index(max_score)
            box = [int(d.bounding_box.origin_x*scale[0]), int(d.bounding_box.origin_y*scale[1]), int((d.bounding_box.origin_x+d.bounding_box.width)*scale[0]), int((d.bounding_box.origin_y+d.bounding_box.height)*scale[1])]
            box = [0 if i<0 else i for i in box]
            obj = {
                "box": box,
                "class": d.classes[max_index].class_name, 
                "score": d.classes[max_index].score,
                "index": d.classes[max_index].index
            }
            res.append(obj)
        return res  

    def get_consts(self, model):
        assert(model.endswith("tflite"))
        consts_file = model[0:-6]+"py"
        try:
            consts = importfile(consts_file)
            self._classes = consts.CLASSES
            self._classes.sort(key=lambda c: c.lower())
        except:
            pass

        print(self.classes)

