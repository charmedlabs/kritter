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
import re
import numpy as np
import cv2
from threading import Thread, Condition
from kritter import KimageDetected, KimageDetector, render_detected
from tflite_runtime.interpreter import Interpreter

class TFliteDetector(KimageDetector):

    def __init__(self, path, threshold=0.5):
        self.path = path
        self.threshold = threshold
        self.thread = None
        self.thread_enable = False
        self.result = None
        self.image = None
        self.image_cond = Condition()
        self.result_cond = Condition()

        self._load_labels()
        self.interpreter = Interpreter(os.path.join(self.path, "detect.tflite"))
        self.interpreter.allocate_tensors()
        _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']

    def _load_labels(self):
        """Loads the labels file. Supports files with or without index numbers."""
        with open(os.path.join(self.path, "labels.txt"), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.labels = {}
            for row_number, content in enumerate(lines):
                pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
                if len(pair) == 2 and pair[0].strip().isdigit():
                    self.labels[int(pair[0])] = pair[1].strip()
                else:
                    self.labels[row_number] = pair[0].strip()

    def _set_input_tensor(self, image):
        """Sets the input tensor."""
        tensor_index = self.interpreter.get_input_details()[0]['index']
        input_tensor = self.interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image


    def _get_output_tensor(self, index):
        """Returns the output tensor at the given index."""
        output_details = self.interpreter.get_output_details()[index]
        tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))
        return tensor 

    def set_threshold(self, val):
        self.threshold = val  
        
    def detect(self, image, block=True):
        if block:
            return self.run_detect(image)
        else:
            if self.thread is None:
                self.thread = Thread(target=self.run) 
                self.thread_enable = True
                self.thread.start()

            with self.image_cond:
                # Copy image because we will likely be overlaying it with bounding boxes.
                self.image = image.copy() 
                self.image_cond.notify()

            with self.result_cond:
                if self.result is not None:
                    result = self.result 
                    self.result = None
                    self.result_cond.notify()
                    return result
                else:
                    return None

    def run_detect(self, image):

        width = image.shape[1]
        height = image.shape[0]
        image = cv2.resize(image, (self.input_width, self.input_height))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 
        self._set_input_tensor(image)
        self.interpreter.invoke()

        # Get all output details
        boxes = self._get_output_tensor(0)
        classes = self._get_output_tensor(1)
        scores = self._get_output_tensor(2)
        count = int(self._get_output_tensor(3))

        result = []
        for i in range(count):
            if scores[i] >= self.threshold:
                ymin, xmin, ymax, xmax = boxes[i]
                xmin = max(1, int(xmin*width))
                xmax = max(1, int(xmax*width))
                ymin = max(1, int(ymin*height))
                ymax = max(1, int(ymax*height))
                r = KimageDetected(int(classes[i]), self.labels[classes[i]], scores[i], [xmin, ymin, xmax, ymax])
                result.append(r)
        return result


    def run(self):
        while(self.thread_enable):
            with self.image_cond:
                while self.image is None and self.thread_enable:
                    self.image_cond.wait()
                image = self.image
                self.image = None

            self.result = self.run_detect(image)
            with self.result_cond:
                while self.result is not None and self.thread_enable:
                    self.result_cond.wait()

    def close(self):
        if self.thread is not None:
            self.thread_enable = False
            with self.image_cond:
                self.image = []
                self.image_cond.notify()
            with self.result_cond:
                self.result = None
                self.result_cond.notify()
                
            self.thread.join()
            self.thread = None
            self.result = None
            self.image = None
