import os
import logging

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