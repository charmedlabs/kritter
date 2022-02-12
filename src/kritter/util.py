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
import time
import logging
import json
import numpy as np

def set_logger_level(logger, level):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(level)


def file_in_path(path, file):
    for p in path:
        filepath = os.path.join(p, file)
        if os.path.isfile(filepath):
            return filepath
    return None


def get_rgb_color(index=-1, html=False, alpha=None):
    if index==-1:
        index = get_rgb_color.index
        get_rgb_color.index += 1
    index = index % len(get_rgb_color.colors)
    color = get_rgb_color.colors[index]
    if html:
        if alpha:
            return f"rgba({color[0]}, {color[1]}, {color[2]}, {alpha})"
        else:
            return f"rgb({color[0]}, {color[1]}, {color[2]})"
    else:
        return color


get_rgb_color.index = 0
get_rgb_color.colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 128), 
         (128, 255, 0), (0, 128, 255), (255, 0, 255), (255, 128, 0), (0, 255, 128), 
         (128, 0, 255), (0, 255, 255))


def get_bgr_color(index=-1):
    color = list(get_rgb_color(index))
    red = color[0]
    color[0] = color[2]
    color[2] = red
    return color


def file_extension(filename):
    return filename.split(".")[-1].lower()


def valid_image_name(filename):
    ext = file_extension(filename)
    return ext=="jpg" or ext=="png" or ext=="gif"


def valid_video_name(filename):
    ext = file_extension(filename)
    return ext=="mp4"


def valid_media_name(filename):
    return valid_image_name(filename) or valid_video_name(filename)


class JSONEncodeFromNumpy(json.JSONEncoder):
    """
    - Serializes python/Numpy objects via customizing json encoder.
    - **Usage**
        - `json.dumps(python_dict, cls=EncodeFromNumpy)` to get json string.
        - `json.dump(*args, cls=EncodeFromNumpy)` to create a file.json.
    """
    def default(self, obj):
        import numpy
        if isinstance(obj, numpy.ndarray):
            return {
                "_kind_": "ndarray",
                "_value_": obj.tolist()
            }
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj,range):
            value = list(obj)
            return {
                "_kind_" : "range",
                "_value_" : [value[0],value[-1]+1]
            }
        return super(JSONEncodeFromNumpy, self).default(obj)


class JSONDecodeToNumpy(json.JSONDecoder):
    """
    - Deserilizes JSON object to Python/Numpy's objects.
    - **Usage**
        - `json.loads(json_string,cls=DecodeToNumpy)` from string, use `json.load()` for file.
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        import numpy
        if '_kind_' not in obj:
            return obj
        kind = obj['_kind_']
        if kind == 'ndarray':
            return numpy.array(obj['_value_'])
        elif kind == 'range':
            value = obj['_value_']
            return range(value[0],value[-1])
        return obj


class Range:
    def __init__(self, in_range, out_range, inval=None, outval=None):
        if inval is None and outval is None:
            raise RuntimeError("at least one value (inval or outval) needs to be specified")    
        self.in_range = in_range
        self.out_range = out_range
        self._inval = self._outval = None
        if inval is not None:
            self._inval = inval
        if outval is not None:
            self._outval = outval

    @property
    def outval(self):
        if self._outval is None:
            self._outval = self.out_range[0] + (self._inval-self.in_range[0])/(self.in_range[1]-self.in_range[0])*(self.out_range[1]-self.out_range[0])

        return self._outval
    
    @outval.setter
    def outval(self, outval):
        self._outval = outval
        self._inval = None

    @property
    def inval(self):
        if self._inval is None:
            self._inval = self.in_range[0] + (self._outval-self.out_range[0])/(self.out_range[1]-self.out_range[0])*(self.in_range[1]-self.in_range[0])
        return self._inval
    
    @inval.setter
    def inval(self, inval):
        self._inval = inval  
        self._outval = None


# Do a nested dictionary update
def deep_update(d1, d2):
    if all((isinstance(d, dict) for d in (d1, d2))):
        for k, v in d2.items():
            d1[k] = deep_update(d1.get(k), v)
        return d1
    return d2


class FuncTimer:
    def __init__(self, timeout):
        self.active = False
        self.timeout = timeout

    def start(self, func):
        self.t0 = time.time()
        self.func = func
        self.active = True

    def update(self, *argv):
        if not self.active:
            return False
        t = time.time()
        if t-self.t0>self.timeout:
            self.fire()
            return True
        else:
            return False

    def fire(self, *argv):
        self.active = False
        self.func(*argv)

    def cancel(self):
        self.active = False
