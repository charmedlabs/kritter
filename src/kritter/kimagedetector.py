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


def render_detected_box(image, color, label, box, x_offset=0, y_offset=0, font=cv2.FONT_HERSHEY_SIMPLEX, font_size=1.0, font_width=0, line_width=0, padding=0, center=False, bg=True, bg_outline=4, bg_color=(0, 0, 0), bg_3d=False):

    if font_width==0:
        font_width = int(font_size*2 + 0.5)
    if line_width==0:
        line_width = int(font_size*2 + 0.5)
    if padding==0:
        padding = int(font_size*10 + 0.5)
    nudge = int(line_width/2+0.5) 

    w, h = cv2.getTextSize(label, font, font_size, font_width)[0]
    if bg_3d:
        bg_outline = 2
    if bg:
        bg_3d = int(line_width*1.5) if bg_3d else 0
        cv2.rectangle(image, (box[0]+x_offset+bg_3d, box[1]+y_offset+bg_3d), (box[2]+x_offset+bg_3d, box[3]+y_offset+bg_3d), bg_color, line_width*bg_outline)
        if not center:
            cv2.rectangle(image, (box[0]+x_offset-bg_outline+bg_3d, box[1]+y_offset-bg_outline-nudge+bg_3d), (box[0]+x_offset+w+2*padding+bg_outline+bg_3d, box[1]+y_offset+h+2*padding+bg_outline+bg_3d), bg_color, -1)

    cv2.rectangle(image, (box[0]+x_offset, box[1]+y_offset), (box[2]+x_offset, box[3]+y_offset), color, line_width)
    if not center:
        cv2.rectangle(image, (box[0]+x_offset, box[1]+y_offset-nudge), (box[0]+x_offset+w+2*padding, box[1]+y_offset+h+2*padding), color, -1)

    if bg:
        bg_3d = int(font_width*1.5) if bg_3d else 0
    if center:
        if bg:
            cv2.putText(image, label, (int((box[0]+x_offset+box[2]+x_offset)/2-w/2+bg_3d), int((box[1]+y_offset+box[3]+y_offset)/2+h/4+bg_3d)), font, font_size, bg_color, font_width*bg_outline)

        cv2.putText(image, label, (int((box[0]+x_offset+box[2]+x_offset)/2-w/2), int((box[1]+y_offset+box[3]+y_offset)/2+h/4)), font, font_size, color, font_width)
    else:
        if bg:
            cv2.putText(image, label, (box[0]+x_offset+padding+bg_3d, box[1]+y_offset+padding+h+bg_3d), font, font_size, bg_color, font_width*bg_outline)
        cv2.putText(image, label, (int(box[0]+x_offset+padding), int(box[1]+y_offset+padding+h)), font, font_size, (255, 255, 255), font_width)


def render_detected(image, detected, disp_confidence=True, x_offset=0, y_offset=0, font=cv2.FONT_HERSHEY_SIMPLEX, font_size=1.0, font_width=0, line_width=0, padding=0, center=False, bg=True, bg_outline=4, bg_color=(0, 0, 0), bg_3d=False):

    for i in detected:
        if disp_confidence:
            txt = i.label + ' %.2f' % i.score
        else:
            txt = i.label
        color = get_bgr_color(i.index)
        render_detected_box(image, color, txt, i.box, x_offset, y_offset, font, font_size, font_width, line_width, padding, center, bg, bg_outline, bg_color, bg_3d)


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