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
import time
import numpy as np

class DetectionPicker:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.info = {}

    def _value(self, det, image):
        # If score0 is in det, it means the the current frame has object in it.  
        # We only want to consider pictures with detected object in it, not
        # pictures where object has disappeared (for example).
        if 'score0' in det:
            try:
                box = det['box']
                area = (box[2]-box[0])*(box[3]-box[1])
                # Crop object out of image
                box = image[box[1]:box[3], box[0]:box[2], :]
                # Calculate sharpness of image by calculating edges on green channel
                # and averaging.
                c = cv2.Canny(box[:, :, 1], 50, 250)
                sharpness = np.mean(c)
                return area*sharpness
            except:
                pass
        
        return 0

    def get_regs_deregs(self):
        return self.regs, self.deregs

    def update(self, image, dets):
        t = time.time()

        # Calculate registrations and deregistrations
        ikeys = set(self.info.keys())
        dkeys = set(dets.keys())
        # Determine new objects
        regs = dkeys-ikeys
        self.regs = {i: dets[i] for i in regs}
        # Determine which object(s) we deregistered, if any.
        deregs = ikeys-dkeys
        self.deregs = {i: self.info[i][1] for i in deregs}

        for k, v in dets.items():
            try:
                if self.info[k][3]==0:
                    continue
            except:
                pass
            v['box'] = v['box'][0:4].tolist() # make list, get rid of extra bits
            value = self._value(v, image)
            try:
                # Update class to most recent because it's the most accurate.
                self.info[k][1]['class'] = v['class']
                # If value exceeds current max, set info.
                if value>self.info[k][0]:
                    self.info[k][0:3] = [value, v, image]
            except:
                self.info[k] = [value, v, image, t]

        # Determine which objects have timed-out, if any.
        timeouts = []
        for k, v in self.info.items():
            if v[3]!=0 and t-v[3]>self.timeout and k not in deregs:
                v[3] = 0
                timeouts.append(k)

        res = []
        # Go through deregistered objects, add to result, but only if it wasn't a timeout
        for i in deregs:
            if self.info[i][3]!=0: # If i isn't a timeout
                res.append((self.info[i][2], self.info[i][1]))
            del self.info[i]
        # Go through timeouts, add to result
        for i in timeouts:
            res.append((self.info[i][2], self.info[i][1]))

        return res
