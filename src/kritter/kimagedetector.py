import numpy as np
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


def render_detected(image, detected, disp_confidence=True, x_offset=0, y_offset=0, font=cv2.FONT_HERSHEY_SIMPLEX, font_size=1.0, font_width=2, line_thickness=3):

    for i in detected:
        if disp_confidence:
            txt = i.label + ' %.2f' % i.score
        else:
            txt = i.label
        color = get_bgr_color(i.index)
        cv2.rectangle(image, (i.box[0]+x_offset, i.box[1]+y_offset), (i.box[2]+x_offset, i.box[3]+y_offset), color, line_thickness)
        w, h = cv2.getTextSize(txt, font, font_size, font_width)[0]
        cv2.putText(image, txt, (int((i.box[0]+x_offset+i.box[2]+x_offset)/2-w/2), int((i.box[1]+y_offset+i.box[3]+y_offset)/2+h/4)), font, font_size, color, font_width)


# Malisiewicz et al., adapted from pyimagesearch.com
def non_max_suppression(boxes, overlapThresh=0.5):
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []
    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")
    # initialize the list of picked indexes 
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]
        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlapThresh)[0])))
    # return only the bounding boxes that were picked using the
    # integer data type
    return pick