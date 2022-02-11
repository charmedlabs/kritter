#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

from threading import Thread
from kritter import Kritter, Kvideo, Camera 


# Frame grabbing thread
def grab(video, stream, run):
    while run():
        # Get frame
        frame = stream.frame()
        # Send frame
        video.push_frame(frame)


if __name__ == "__main__":
    # Create and start camera.
    camera = Camera()
    stream = camera.stream()

    # Create Kritter server.
    kapp = Kritter()
    # Create video component.
    video = Kvideo()
    # Add video component to layout.
    kapp.layout = video

    # Run camera grab thread.
    run_grab = True
    grab_thread = Thread(target=grab, args=(video, stream, lambda: run_grab))
    grab_thread.start()

    # Run Kritter server, which blocks.
    kapp.run()
    run_grab = False
