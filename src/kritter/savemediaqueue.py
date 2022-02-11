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
import json
from time import sleep
from threading import Thread
import cv2
import datetime
from .kstoremedia import KstoreMedia
from .util import file_extension, valid_image_name, valid_video_name, valid_media_name

UPLOADED = "U"
KEEP = 100

def basename(filename):
    return filename.split(".")[0]

class SaveMediaQueue(KstoreMedia):

    def __init__(self, store_media, path="", keep=KEEP):
        super().__init__()
        self.store_media = store_media
        self.path = path
        self.keep = keep
        if not os.path.isdir(self.path):
            os.system(f"mkdir -p {self.path}")
        self.thread_ = Thread(target=self.thread)
        self.run_thread = True
        self.thread_.start()

    def close(self):
        self.run_thread = False
        self.thread_.join()

    def thread(self):
        while self.run_thread:
            uploaded = []
            # find all images in path
            files = os.listdir(self.path)
            files = sorted(files)
            for file in files:
                if not valid_media_name(file):
                    continue
                if not self.run_thread:
                    break
                parts = file.split('.')
                # if file looks legit and it doesn't have the uploaded string, upload
                if len(parts)>=2:
                    if parts[0][-1]==UPLOADED:
                        uploaded.append(file)
                    else:
                        print('Uploading', file)
                        file = os.path.join(self.path, file)                        
                        try:
                            metadata = self._load_metadata(file)
                            if self.store_media.store_image_file(file, metadata['album'], metadata['desc']):
                                # if uploaded successfully, add uploaded string before extension
                                parts[0] += UPLOADED
                                new_filename = '.'.join(parts)
                                new_filename = os.path.join(self.path, new_filename)
                                os.rename(file, new_filename)
                                print('Done uploading ', file)
                            else:
                                print(f"Error uploading {file} to {metadata['album']}")
                        except Exception as e:
                            print('Exception uploading', file, e)
            # clean up files
            if len(uploaded)>self.keep:
                uploaded = sorted(uploaded)
                for i in range(len(uploaded)-self.keep):
                    file = os.path.join(self.path, uploaded[i])
                    try:
                        os.remove(file)
                        os.remove(basename(file)[0:-1]+".json")
                    except:
                        pass

            sleep(1)

    def _get_filename(self, ext):
        return os.path.join(self.path, datetime.datetime.now().strftime(f"%Y_%m_%d_%H_%M_%S_%f.{ext}"))

    def _save_metadata(self, filename, album, desc):
        data = {"album": album, "desc": desc}
        with open(f'{basename(filename)}.json', 'w') as file:
            json.dump(data, file)   

    def _load_metadata(self, filename):
        with open(f'{basename(filename)}.json') as file:
            return json.load(file)   

    def store_image_file(self, filename, album="", desc=""):
        if not valid_image_name(filename):
            raise RuntimeError(f"File {filename} isn't correct media type.")
        new_filename = self._get_filename(file_extension(filename))
        self._save_metadata(new_filename, album, desc)
        # perform rename so we don't accidentally try to upload a half-written file
        os.rename(filename, new_filename)

    def store_video_file(self, filename, album="", desc=""):
        if not valid_video_name(filename):
            raise RuntimeError(f"File {filename} isn't correct media type.")
        new_filename = self._get_filename(file_extension(filename))
        self._save_metadata(new_filename, album, desc)
        # perform rename so we don't accidentally try to upload a half-written file
        os.rename(filename, new_filename)
