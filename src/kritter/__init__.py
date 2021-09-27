import json
import os

_basepath = os.path.dirname(__file__)

# Set IPA module path for libcamera since we're using a local copy of libcamera
os.environ['LIBCAMERA_IPA_MODULE_PATH'] = _basepath

from .about import __version__
from .util import file_in_path, set_logger_level, get_rgb_color, get_bgr_color
from .kcamera import Camera 
from .kencoder import Encoder
from .streamer import Streamer
from .kcomponent import Kcomponent, default_style 
from .kvideo import Kvideo
from .kritter import Kritter, run_kterm, PORT, BASE_DIR, MEDIA_DIR
from .kcheckbox import Kcheckbox 
from .kdropdown import Kdropdown  
from .kslider import Kslider  
from .kbutton import Kbutton
from .kdialog import Kdialog, KyesNoDialog, KokDialog, KsideMenuItem
from .ktext import Ktext
from .ktextbox import KtextBox
from .kradio import Kradio
from .klogin import Klogin, PMASK_MAX, PMASK_MIN
from .execterm import ExecTerm
from .kimagedetector import KimageDetected, KimageDetector, render_detected

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
