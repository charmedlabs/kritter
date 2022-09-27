#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

from kritter import get_color
import cv2 
        
class KimageDetector:

    def __init__(self):
        self._classes = []

    def detect(self, image, threshold=None):
        pass

    def classes(self):
        return self._classes

from threading import Thread, Lock

class KimageDetectorThread(KimageDetector):
    def __init__(self, detector):
        self.detector = detector 
        self.lock = Lock()
        self.thread = None
        self.result = None

    def detect(self, image, threshold=None):
        self.image = image
        self.threshold = threshold
        if not self.thread:
            self.run_thread = True
            self.thread = Thread(target=self.run)
            self.thread.start()
        with self.lock:
            result = self.result 
            self.result = None
        return result 

    def run(self):
        while self.run_thread:
            active_image = self.image
            result = self.detector.detect(active_image, self.threshold)
            with self.lock:
                self.result = result, active_image

    def close(self):
        if self.thread:
            self.run_thread = False
            self.thread.join()

def _hash(string):
    val = 7
    for c in string:
        val += val*7 + ord(c)
    return val 

def render_detected_box(overlay, color, label, box, font="sans-serif", font_size=12, line_width=2, scale=1):
    html_color = f'rgb({color[0]},{color[1]},{color[2]}' 
    overlay.draw_rect(*box[0:4], fillcolor="rgba(0,0,0,0)", line=dict(color=html_color, width=line_width), id='render_detected_box')

    offset = int(line_width/2)
    xoffset = 0 if box[0]<offset else -offset
    if box[1]<font_size*2/scale:
        yoffset = 0 if box[1]<offset else -offset
        yanchor = "top"
    else:
        yoffset = offset
        yanchor = "bottom"
    # Perform an elaborate calculation to determine if we should have white or black text
    color_calc = color[0]*0.8+color[1]*1.4+color[2]*0.5
    text_color = "white" if color_calc<350 else "black"

    overlay.draw_text(box[0]+xoffset, box[1]+yoffset, label, font=dict(family=font, size=font_size, color=text_color), fillcolor=html_color, xanchor="left", yanchor=yanchor, id='render_detected_box')

def render_detected(overlay, detected, label_format=None, font="sans-serif", font_size=12, line_width=2, scale=1):
    overlay.draw_clear(id='render_detected_box')
    if label_format is None:
        label_format = lambda key, det : f"{det['class']} {det['score']*100:.0f}%" 

    if isinstance(detected, list):
        for i in detected:
            txt = label_format(None, i)
            try:
                index = i['index']
            except:
                index = _hash(i['class'])
            color = get_color(index)
            render_detected_box(overlay, color, txt, i['box'], font, font_size, line_width, scale)

    if isinstance(detected, dict):
        for i, v in detected.items():
            txt = label_format(i, v)
            try:
                index = v['index']
            except:
                index = _hash(v['class'])
            color = get_color(index)
            render_detected_box(overlay, color, txt, v['box'], font, font_size, line_width, scale)

    return overlay.out_draw()


def render_detected_box_image(image, color, label, box, x_offset=0, y_offset=0, font=cv2.FONT_HERSHEY_SIMPLEX, font_size=1.0, font_width=0, line_width=0, padding=0, center=False, label_on_top=True, bg=True, bg_outline=4, bg_color=(0, 0, 0), bg_3d=False):

    if font_width==0:
        font_width = int(font_size*2 + 0.5)
    if line_width==0:
        line_width = int(font_size*2 + 0.5)
    if padding==0:
        padding = int(font_size*10 + 0.5)
    nudge = int(line_width/2+0.5) 

    w, h = cv2.getTextSize(label, font, font_size, font_width)[0]
    # If label is off the top of the screen, put label below top line.
    if box[1]<h+2*padding:
        label_on_top = False
    if bg_3d:
        bg_outline = 2
    if bg:
        bg_3d = int(line_width*1.5) if bg_3d else 0
        ow = line_width*bg_outline
        ow2 = int(ow/2 + 0.5) 
        cv2.rectangle(image, (box[0]+x_offset+bg_3d, box[1]+y_offset+bg_3d), (box[2]+x_offset+bg_3d, box[3]+y_offset+bg_3d), bg_color, ow)
        if not center:
            if label_on_top:
                cv2.rectangle(image, (box[0]+x_offset-ow2+bg_3d-nudge, box[1]+y_offset-ow2-h-2*padding+bg_3d), (box[0]+x_offset+w+2*padding+ow2+bg_3d, box[1]+y_offset+ow2+nudge+bg_3d), bg_color, -1)
            else:
                cv2.rectangle(image, (box[0]+x_offset-ow2+bg_3d, box[1]+y_offset-ow2-nudge+bg_3d), (box[0]+x_offset+w+2*padding+ow2+bg_3d, box[1]+y_offset+h+2*padding+ow2+bg_3d), bg_color, -1)

    cv2.rectangle(image, (box[0]+x_offset, box[1]+y_offset), (box[2]+x_offset, box[3]+y_offset), color, line_width)
    if not center:
        if label_on_top:
            cv2.rectangle(image, (box[0]+x_offset-nudge, box[1]+y_offset-h-2*padding), (box[0]+x_offset+w+2*padding, box[1]+y_offset+nudge), color, -1)
        else:
            cv2.rectangle(image, (box[0]+x_offset, box[1]+y_offset-nudge), (box[0]+x_offset+w+2*padding, box[1]+y_offset+h+2*padding), color, -1)


    if bg:
        bg_3d = int(font_width*1.5) if bg_3d else 0
    if center:
        if bg:
            cv2.putText(image, label, (int((box[0]+x_offset+box[2]+x_offset)/2-w/2+bg_3d), int((box[1]+y_offset+box[3]+y_offset)/2+h/4+bg_3d)), font, font_size, bg_color, font_width*bg_outline)

        cv2.putText(image, label, (int((box[0]+x_offset+box[2]+x_offset)/2-w/2), int((box[1]+y_offset+box[3]+y_offset)/2+h/4)), font, font_size, color, font_width)
    else:
        hoffs = -padding if label_on_top else padding+h
        if bg:
            cv2.putText(image, label, (box[0]+x_offset+padding+bg_3d, box[1]+y_offset+hoffs+bg_3d), font, font_size, bg_color, font_width*bg_outline)
        cv2.putText(image, label, (int(box[0]+x_offset+padding), int(box[1]+y_offset+hoffs)), font, font_size, (255, 255, 255), font_width)

def render_detected_image(image, detected, label_format=None, x_offset=0, y_offset=0, font=cv2.FONT_HERSHEY_SIMPLEX, font_size=1.0, font_width=0, line_width=0, padding=0, center=False, label_on_top=True, bg=True, bg_outline=4, bg_color=(0, 0, 0), bg_3d=False):

    if label_format is None:
        label_format = lambda key, det : f"{det['class']} {det['score']*100:.0f}%" 
    _detected = detected.values() if isinstance(detected, dict) else detected
    if isinstance(detected, list):
        for i in detected:
            txt = label_format(None, i)
            try:
                index = i['index']
            except:
                index = _hash(i['class'])
            color = get_color(index, bgr=True)
            render_detected_box_image(image, color, txt, i['box'], x_offset, y_offset, font, font_size, font_width, line_width, padding, center, label_on_top, bg, bg_outline, bg_color, bg_3d)

    if isinstance(detected, dict):
        for i, v in detected.items():
            txt = label_format(i, v)
            try:
                index = v['index']
            except:
                index = _hash(v['class'])
            color = get_color(index, bgr=True)
            render_detected_box_image(image, color, txt, v['box'], x_offset, y_offset, font, font_size, font_width, line_width, padding, center, label_on_top, bg, bg_outline, bg_color, bg_3d)


