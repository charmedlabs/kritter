#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import json
import os

_basepath = os.path.dirname(__file__)

# Set IPA module path for libcamera since we're using a local copy of libcamera
os.environ['LIBCAMERA_IPA_MODULE_PATH'] = _basepath

from .about import __version__
from .util import file_in_path, set_logger_level, get_rgb_color, get_bgr_color, file_extension, valid_image_name, valid_video_name, valid_media_name, JSONEncodeFromNumpy, JSONDecodeToNumpy, Range, deep_update, FuncTimer
from .camera import Camera 
from .kencoder import Encoder
from .streamer import Streamer
from .kcomponent import Kcomponent, default_style 
from .kvideo import Kvideo
from .kritter import Kritter, run_kterm, PORT, BASE_DIR, MEDIA_DIR
from .kcheckbox import Kcheckbox 
from .kdropdown import Kdropdown 
from .kdropdownmenu import KdropdownMenu 
from .kslider import Kslider  
from .kbutton import Kbutton
from .kdialog import Kdialog, KyesNoDialog, KokDialog, KprogressDialog, KsideMenuItem
from .ktext import Ktext
from .ktextbox import KtextBox
from .kradio import Kradio
from .klogin import Klogin, PMASK_MAX, PMASK_MIN
from .execterm import ExecTerm
from .kimagedetector import KimageDetected, KimageDetector, render_detected, render_detected_box, non_max_suppression
from .gcloud import Gcloud
from .gpstoremedia import GPstoreMedia
from .savemediaqueue import SaveMediaQueue
from .proxy import Proxy 
from .telegramclient import TelegramClient
from .ktextvisor import KtextVisor
from .configfile import ConfigFile
from .importconfig import import_config

_comp_filepath = os.path.abspath(os.path.join(_basepath, 'kvideocomp', 'package-info.json'))
with open(_comp_filepath) as f:
    package = json.load(f)

__version__ = package['version']

_js_dist = [
    {
        'relative_package_path': 'kvideocomp/kvideocomp.min.js',
        'namespace': 'kritter'
    },
    {
        'relative_package_path': 'kvideocomp/kvideocomp.min.js.map',
        'namespace': 'kritter',
        'dynamic': True
    }
]
