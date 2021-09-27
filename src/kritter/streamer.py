import asyncio
import json
import logging
import time
import fractions
import contextvars
import cv2
from queue import Queue, Full, Empty 
from threading import Thread, Lock
import aiortc.rtcrtpsender as rtcrtpsender
from aiortc.codecs import CODECS
from aiortc.mediastreams import MediaStreamTrack, VIDEO_TIME_BASE, convert_timebase
from aiortc import RTCPeerConnection, RTCSessionDescription
import aiortc.codecs.base
from quart import Response, request, Quart, jsonify
from .h264 import H264Encoder

MAX_TIMEOUTS = 3
BITRATE_WINDOW = 2 # seconds
MIN_FRAMERATE = 1 # frames/sec
DEFAULT_BITRATE = 3000000 # Mbps
# Frameperiod adjustment rate -- lower means slower
FRAMEPERIOD_ADJ_RATE = 0.5
QUEUE_TIMEOUT = 1 # seconds

MIN_FRAMEPERIOD = 1/MIN_FRAMERATE # Change MIN_FRAMERATE instead

logger = logging.getLogger(__name__)
from .util import set_logger_level
#set_logger_level(logger, logging.DEBUG)


index_html = \
"""
<html>
<head>
    <title>Pi Streamer</title>
    <script src="client.js"></script>
</head>
<body>
<div>
    <video width="640" height="480" id="video" autoPlay="true" playsInline="true" muted="true"></video>
</div>
</body>
</html>
"""

client_js = \
"""
var pc = null;

function connect() {
    start();
}

window.addEventListener("load", connect);

function negotiate() {
    pc.addTransceiver('video', {direction: 'recvonly'});
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        return pc.setRemoteDescription(answer);
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    //config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];

    pc = new RTCPeerConnection(config);

    // connect video
    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        }
    });

    negotiate();
}

function stop() {

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}
"""


def fps():
    fps.n += 1
    if fps.t0==0:
        fps.t0 = time.time()
    t = time.time()
    if t-fps.t0 > 1:
        rate = fps.n/(t-fps.t0)
        print("{:.2f} fps".format(rate))
        fps.t0 = t
        fps.n = 0

fps.t0 = fps.n = 0


class Encoder(aiortc.codecs.base.Encoder):
    def __init__(self, framerate=30):
        self.streams = []
        self.mr_frame = None
        self.force_keyframe = False
        self.encoder = H264Encoder(bitrate=DEFAULT_BITRATE)
        self.frameperiod = 1/framerate;
        self.current_frameperiod = self.frameperiod
        self.target_bitrate_t0 = None
        self._target_bitrate = None
        self.bitrate_t0 = None
        self.bitrate_n = None
        self.actual_bitrate = None
        self.thread = None
        self.slock = Lock()
        self.flock = Lock()

    def add_stream(self, stream):
        self.slock.acquire()
        self.streams.append(stream)
        self.slock.release()
        logger.debug('add_stream ' + str(len(self.streams)))
        if len(self.streams)==1:
            self.thread = Thread(target=self.run)
            self.thread.start()

    def remove_stream(self, stream):
        self.slock.acquire()
        self.streams.remove(stream)
        self.slock.release()
        logger.debug('remove_stream ' + str(len(self.streams)))

    def timestamp(self, pts):
        time_base = fractions.Fraction(1, 1)
        return convert_timebase(pts, time_base, VIDEO_TIME_BASE)

    def encode(self, stream, force_keyframe):
        self.flock.acquire()
        if (force_keyframe):
            self.force_keyframe = True
        self.flock.release()
        # Note, we might get a stop on the stream while we're waiting on the queue. 
        # The timeout is a bit lazy, but it will never cause a deadlock.
        for i in range(MAX_TIMEOUTS):
            if stream in self.streams: 
                try:
                    return stream.queue.get(timeout=QUEUE_TIMEOUT)
                except Empty:
                    logger.debug("queue get timeout")
            else:    
                break
        return ([], self.timestamp(stream.pts))

    def push_frame(self, frame):
        self.mr_frame = frame

    def update_actual_bitrate(self, data):
        if self.bitrate_t0 is None:
            self.bitrate_t0 = time.time()
            self.bitrate_n = 0
        for p in data:
            self.bitrate_n += len(p)*8
        t = time.time()
        # Note, if we update the bitrate faster than 1 Hz, we'll get into a situation
        # Where the I frames won't average across windows. 
        if t-self.bitrate_t0>BITRATE_WINDOW:
            self.actual_bitrate = self.bitrate_n/(t-self.bitrate_t0)
            logger.debug("bitrate: " + str(int(self.actual_bitrate)))
            self.bitrate_t0 = t
            self.bitrate_n = 0

    @property
    def target_bitrate(self):
        return self._target_bitrate

    @target_bitrate.setter 
    def target_bitrate(self, val):
        t = time.time()
        # Find minimum bitrate within a time window.
        # Note, each client/browser will send REMB bitrate updates at 
        # a rate of about 2 Hz, so as long as the time period is greater
        # than say 0.5s, we'll get the minimum bitrate of all 
        # clients.  Unfortunately, we can't accomodate all bitrates
        # for all clients because we only have one encoder. But we
        # can accomodate the client with the lowest bandwidth/bitrate
        # abilities, which is why we're interested in the minimum.
        if self.target_bitrate_t0 is None or \
            t-self.target_bitrate_t0>BITRATE_WINDOW or \
            val<self._target_bitrate:
            self.target_bitrate_t0 = t
            self._target_bitrate = val

            if self.actual_bitrate is not None:
                # Calculate frameperiod based on target_bitrate and actual_bitrate. 
                self.current_frameperiod *= 1 - FRAMEPERIOD_ADJ_RATE + FRAMEPERIOD_ADJ_RATE*self.actual_bitrate/self._target_bitrate
                if self.current_frameperiod<self.frameperiod:
                    self.current_frameperiod = self.frameperiod
                elif self.current_frameperiod>MIN_FRAMEPERIOD:
                    self.current_frameperiod = MIN_FRAMEPERIOD 
                logger.debug("framerate {} {} {} {}".format(1/self.current_frameperiod, 
                    1 - FRAMEPERIOD_ADJ_RATE + FRAMEPERIOD_ADJ_RATE*self.actual_bitrate/self._target_bitrate, self.actual_bitrate, self._target_bitrate))           
    
    def encode_and_send(self, frame):
        self.flock.acquire()
        keyframe = self.force_keyframe
        if keyframe:    
            self.force_keyframe = False
        self.flock.release()
        data = self.encoder.encode(frame, keyframe) 
        self.update_actual_bitrate(data)
        self.slock.acquire()
        for s in reversed(self.streams):
            # We are at the mercy of the client browser to grab data in the 
            # queue, so we need a way to detect if things have gone awry. 
            # A series of timeouts is a good way to do this.    
            try:
                s.queue.put((data, self.timestamp(s.pts)), timeout=2*QUEUE_TIMEOUT)
                s.timeouts = 0
            except Full:
                logger.debug("queue put timeout " + str(s.timeouts))
                s.timeouts += 1
                if s.timeouts>=MAX_TIMEOUTS:
                    logger.debug("removing")
                    self.streams.remove(s) 
            s.pts += self.current_frameperiod
        self.slock.release()

    def run(self):
        logger.debug("encoder thread start")
        tn = time.time()
        while len(self.streams)>0:
            frame = self.mr_frame
            if frame is not None:
                self.encode_and_send(frame)
            if logger.level==logging.DEBUG:
                fps()
            # Deal with residual time
            tn += self.current_frameperiod
            t = time.time()
            # Calculate how much time we have left over and sleep that much.
            tsleep = tn - t
            if tsleep>0:
                time.sleep(tsleep)
            else:
                # Give ourselves a break if we're behind
                tn = t 
        logger.debug("encoder thread done")
        self.thread = self.bitrate_t0 = self.target_bitrate_t0 = self._target_bitrate = None
        self.current_frameperiod = self.frameperiod


class StreamTrack(MediaStreamTrack):
    def __init__(self, kind, encoder):
        super().__init__()
        self.kind = kind
        self.encoder = encoder
        self.queue = Queue(maxsize=1) # Queue is only 1 deep to prevent wind-up.
        self.timeouts = 0
        self.pts = 0
        self.encoder.add_stream(self) 

    def stop(self):
        logger.debug("stop")
        super().stop()
        self.encoder.remove_stream(self)

    async def recv(self):
        return self


# Remember original get_encoder routine
__get_encoder = rtcrtpsender.get_encoder

# Remove VP8 from proposed encoders because we don't support
# accelerated VP8, only H264.
for codec in CODECS['video']:
    if codec.mimeType=='video/VP8':
         CODECS['video'].remove(codec)

from aioice.mdns import MDnsProtocol
from typing import Optional

_addr_var = contextvars.ContextVar('addr')

# Note, mdns resolve routine requires that the originator respond to mdns
# requests.  This simply isn't guaranteed under all situations, all architectures, 
# all connection types.  So we assume  that whoever is providing
# the offer will accept the media being provided.  It works fine here because our 
# connection topology is so simple.  
async def resolve(self, hostname: str, timeout: float = 1.0) -> Optional[str]:
    # Just get the address from the context and return. 
    addr = _addr_var.get()
    return addr

# Monkey-patch mdns resolve routine in aioice.
MDnsProtocol.resolve = resolve


class Streamer:

    encoder = None

    def __init__(self, server=None, html=index_html, js=client_js):
        self.pcs = set()
        if Streamer.encoder is None:
            Streamer.encoder = Encoder()
            self.register_encoder()
        else:
            raise runtimeError("only one instance of Streamer is allowed")

        if server is None:
            self.server = Quart("Streamer") 
        else:
            self.server = server

        if html:
            @self.server.route('/')
            async def index():
                return Response(index_html, mimetype='text/html')

        if js:
            @self.server.route('/client.js')
            async def javascript():
                return Response(client_js, mimetype='application/javascript')


        @self.server.route('/offer', methods=['POST'])
        async def offer():
            params = await request.get_json()
            offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

            pc = RTCPeerConnection()
            self.pcs.add(pc)

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                logger.debug("Connection state is {}".format(pc.connectionState))
                if pc.connectionState == "failed":
                    await pc.close()
                    self.pcs.discard(pc)

            # Set address variable for resolve()
            _addr_var.set(request.remote_addr)
            # Create a task so that the contextvar _addr_var gets copied into its own context.
            task = asyncio.create_task(pc.setRemoteDescription(offer))
            await task

            for t in pc.getTransceivers():
                if t.kind == "video":
                    track = StreamTrack('video', Streamer.encoder)
                    pc.addTrack(track)

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            return jsonify(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            )

        @self.server.after_serving
        async def shutdown():
            await self.close_all()

    async def close_all(self):
        # close peer connections
        coros = [pc.close() for pc in self.pcs]
        await asyncio.gather(*coros)
        self.pcs.clear()

    def run(self, host='0.0.0.0', port=5000):
        self.server.run(host=host, port=port, debug=False, use_reloader=False)
        logger.debug("server exitted")

    def push_frame(self, frame):
        # If we get a tuple, assume that it's a (frame, timestamp, index) tuple
        # and toss the timestamp and index.
        if isinstance(frame, tuple):
            frame = frame[0]
        if len(frame.shape)==2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        if len(frame.shape)!=3 and frame.shape[2]!=3:
            raise RuntimeError("Frames need to be 3 dimensions -- width x height x 3 channels")   
        Streamer.encoder.push_frame(frame)

    def register_encoder(self):
        def _get_encoder(codec):
            mimeType = codec.mimeType.lower()

            if mimeType == "video/h264":
                return Streamer.encoder
            else:
                return __get_encoder(codec)

        # Do some monkey-patching so rtcrtpsender grabs our encoder
        rtcrtpsender.get_encoder = _get_encoder
