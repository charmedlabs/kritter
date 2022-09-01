#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
from kritter import KimageClassifier

class TFliteClassifier(KimageClassifier):
    def __init__(self, model):
        base_options = core.BaseOptions(file_name=model, use_coral=False, num_threads=4)
        classification_options = processor.ClassificationOptions(max_results=3, score_threshold=0)
        options = vision.ImageClassifierOptions(base_options=base_options, classification_options=classification_options)
        self.classifier = vision.ImageClassifier.create_from_options(options)

    def classify(self, image):
        res = []
        image = cv2.flip(image, 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_tensor = vision.TensorImage.create_from_array(image)
        categories = self.classifier.classify(input_tensor)
        for c in categories.classifications[0].classes:
            _class = {"class": c.class_name, "score": c.score}
            res.append(_class)
        return res