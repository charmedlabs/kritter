#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import dash_devices
from dash_devices.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from kritter import Camera, Streamer
from kritter.kvideocomp import KvideoComp
from threading import Thread

app = dash_devices.Dash(__name__)

app.layout = html.Div([
    KvideoComp(id="video", width=640, height=480)
])


# Frame grabbing thread
def grab(streamer, stream, run):
    while run():
        frame = stream.frame()
        streamer.push_frame(frame)


if __name__ == "__main__":
    # Set up camera and streamer
    camera = Camera()
    stream = camera.stream()
    streamer = Streamer(server=app.server, html=None, js=None)
    # Start frame grabbing thread
    run_grab = True
    grab_thread = Thread(target=grab, args=(streamer, stream, lambda: run_grab))
    grab_thread.start()

    app.run_server(debug=True, host='0.0.0.0', port=5000)    # Exit grab thread
    run_grab = False

