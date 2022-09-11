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
import cv2

TEMPDIR = "/tmp/"

class KstoreMedia:

    def __init__(self):
        self.tempfile = os.urandom(8).hex().upper()
        # Each instantiation gets its own temp files.  This means one thread per object. 
        self.tempimage = os.path.join(TEMPDIR, self.tempfile+".jpg")
        self.tempvideo = os.path.join(TEMPDIR, self.tempfile+".mp4")

    def store_image_array(self, array, album="", desc="", data={}):
        cv2.imwrite(self.tempimage, array)
        return self.store_image_file(self.tempimage, album, desc, data)

    def store_image_file(self, filename, album="", desc="", data={}, thumbnail=None):
        pass

    def store_video_stream(self, stream, fps=30, album="", desc="", data={}, thumbnail=False):
        frame = stream.frame()
        if thumbnail:
            cv2.imwrite(self.tempimage, frame[0])
            thumbnail = self.tempimage
        else:
            thumbnail = None

        if not frame:
            return
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        writer = cv2.VideoWriter(self.tempvideo, fourcc, fps, (frame[0].shape[1], frame[0].shape[0]))
        while frame:
            print(f"{frame[2]+1} of {stream.len()}")
            writer.write(frame[0])
            frame = stream.frame()
        writer.release()
        print(f"Wrote {stream.len()} frames") # Note, can't just print the stream.len() because it may not be ready yet.   
        return self.store_video_file(self.tempvideo, album, desc, data, thumbnail)

    def store_video_file(self, filename, album="", desc="", data={}, thumbnail=None):
        pass
