from abc import ABC, abstractmethod 
from kritter import get_bgr_color
import cv2 

class KimageDetector(ABC):

    # Return array of KimageDetected
    @abstractmethod
    def detect(self, image, block=True):
        pass

    def open(self):
        pass

    def close(self):
        pass


class KimageDetected:

    def __init__(self, index, label, score, box):
        self.index = index
        self.label = label
        self.score = score
        self.box = box


def render_detected(image, detected, disp_confidence=True):
    line_thickness = 3
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 1.0
    font_width = 2

    for i in detected:
        if disp_confidence:
            txt = i.label + ' %.2f' % i.score
        else:
            txt = i.label
        color = get_bgr_color(i.index)
        cv2.rectangle(image, (i.box[0], i.box[1]), (i.box[2], i.box[3]), color, line_thickness)
        w, h = cv2.getTextSize(txt, font, font_size, font_width)[0]
        cv2.putText(image, txt, (int((i.box[0]+i.box[2])/2-w/2), int((i.box[1]+i.box[3])/2+h/4)), font, font_size, color, font_width)

