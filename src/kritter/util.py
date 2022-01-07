import os
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

def get_rgb_color(index=-1):
    if index==-1:
        index = get_rgb_color.index
        get_rgb_color.index += 1
    index = index % len(get_rgb_color.colors)
    return get_rgb_color.colors[index]

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
        return super(EncodeFromNumpy, self).default(obj)


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
