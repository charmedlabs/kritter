from kritter import KimageDetector, KimageDetected
from threading import Thread, Condition
import numpy as np
import tensorflow as tf
import cv2
import os
from .label_map_util import load_labelmap, convert_label_map_to_categories, create_category_index

class TFDetector(KimageDetector):

    def __init__(self, path, min_threshold=0.5):
        self.path = path
        self.min_threshold = min_threshold
        self.thread = None
        self.result = None
        self.image = None
        self.image_cond = Condition()
        self.result_cond = Condition()

    def open(self):
        label_map_path = os.path.join(self.path, "labelmap.pbtxt")
        label_map = load_labelmap(label_map_path)
        categories = convert_label_map_to_categories(label_map, max_num_classes=1000, use_display_name=True)
        self.category_index = create_category_index(categories)

        # Load the Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            graph_path = os.path.join(self.path, "frozen_inference_graph.pb")
            with tf.io.gfile.GFile(graph_path, "rb") as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.compat.v1.Session(graph=detection_graph)


        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        print('loaded')

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

        if self.sess:
            self.sess.close()

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
        image = cv2.resize(image, (300, 300))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.expand_dims(image, axis=0)
        boxes, scores, classes, num = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image})
        items = self.threshold(width, height, np.squeeze(scores), np.squeeze(boxes), np.squeeze(classes).astype(np.int32))
        return items

    def threshold(self, width, height, scores, boxes, classes):
        items = []
        for i, s in enumerate(scores):
            if s>=self.min_threshold:
                items.append(KimageDetected(classes[i], self.category_index[classes[i]]['name'], scores[i], [int(boxes[i][1]*width), int(boxes[i][0]*height), 
                    int(boxes[i][3]*width), int(boxes[i][2]*height)]))
        return items    

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
