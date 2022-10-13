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
import cv2
from threading import Timer
from .util import temp_file
PROGRESS_TIMEOUT = 2 # seconds

class KstoreMedia:

    def __init__(self):
        pass

    def store_image_array(self, array, album="", desc="", data={}):
        temp = temp_file("jpg")
        cv2.imwrite(temp, array)
        return self.store_image_file(temp, album, desc, data)

    def store_image_file(self, filename, album="", desc="", data={}, thumbnail=None):
        pass

    def store_video_stream(self, stream, fps=30, album="", desc="", data={}, thumbnail=False, progress_callback=None):
        frame = stream.frame()
        if thumbnail:
            thumbnail = temp_file("jpg")
            cv2.imwrite(thumbnail, frame[0])
        else:
            thumbnail = None

        if not frame:
            return
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        temp_video = temp_file("mp4")
        writer = cv2.VideoWriter(temp_video, fourcc, fps, (frame[0].shape[1], frame[0].shape[0]))

        percent = 0
        if progress_callback:
            def progress():
                if frame:
                    progress_callback(percent)
                    Timer(PROGRESS_TIMEOUT, progress).start() 
                else: # frame is None, meaning we're done (sorta)
                    progress_callback(99)
            Timer(PROGRESS_TIMEOUT, progress).start()

        while frame:
            percent = int((frame[2]+1)/stream.len()*100-.1) # max-out at 99
            print(f"{frame[2]+1} of {stream.len()} ({percent}%)")
            writer.write(frame[0])
            frame = stream.frame()
        writer.release()
        print(f"Wrote {stream.len()} frames") 
        return self.store_video_file(temp_video, album, desc, data, thumbnail)

    def store_video_file(self, filename, album="", desc="", data={}, thumbnail=None):
        pass

    def get_share_url(self, album):
        pass
