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
from kritter import Camera, Streamer

# Frame grabbing thread
def grab(streamer, stream, run):
    while run():
        frame = stream.frame()
        streamer.push_frame(frame)


if __name__ == "__main__":
    # Set up camera and streamer
    camera = Camera()
    stream = camera.stream()
    streamer = Streamer()
    # Start frame grabbing thread
    run_grab = True
    grab_thread = Thread(target=grab, args=(streamer, stream, lambda: run_grab))
    grab_thread.start()

    # Run streamer until we get interrupted while frame grabber runs 
    # in its own thread.
    streamer.run()
    # Exit grab thread
    run_grab = False
