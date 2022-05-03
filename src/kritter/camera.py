#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

from .kcamera import Camera as Camera_

class Camera(Camera_):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        modes = super().getmodes()
        self.mode_info = {
            '320x240x10bpp (cropped)': {"pixelsize": (2*1332/320, 2*1332/320), "crop": (1332/2028, 990/1520), "offset": (0, 0.16), "bitdepth": 10}, 
            '640x480x10bpp (cropped)': {"pixelsize": (2*1332/640, 2*1332/640), "crop": (1332/2028, 990/1520), "offset": (0, 0.16), "bitdepth": 10},
            '768x432x10bpp': {"pixelsize": (2*2028/768, 2*2028/768), "crop": (1, 1080/1520), "offset": (0, 0.16), "bitdepth": 10},
            '1280x720x10bpp': {"pixelsize": (2*2028/1280, 2*2028/1280), "crop": (1, 1080/1520), "offset": (0, 0.16), "bitdepth": 10},
            '1280x960x10bpp (cropped)': {"pixelsize": (2*1332/1280, 2*1332/1280), "crop": (1332/2028, 990/1520), "offset": (0, 0.16), "bitdepth": 10},
            '1920x1080x10bpp': {"pixelsize": (2*2028/1920, 2*2028/1920), "crop": (1, 1080/1520), "offset": (0, 0.16), "bitdepth": 10},
            '2016x1520x10bpp': {"pixelsize": (2, 2), "crop": (2016/2028, 1), "offset": (0, 0), "bitdepth": 10}
        }
        assert(set(modes)==set(self.mode_info.keys()))

        save_mode = self.mode
        for m in modes:
            self.mode = m 
            framerate = self.min_framerate, self.max_framerate
            self.mode_info[m]['resolution'] = self.resolution
            self.mode_info[m]['framerate'] = framerate

        self.mode = save_mode


    def getmodes(self):
        return self.mode_info 


nc = Camera()
