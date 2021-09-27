import fractions
import logging
import math
import time
from struct import pack, unpack_from
from typing import Iterator, List, Tuple
import kritter
import cv2

logger = logging.getLogger(__name__)
from .util import set_logger_level
set_logger_level(logger, logging.DEBUG)

MAX_BITRATE = 3000000  # 3 Mbps
DEFAULT_BITRATE = MAX_BITRATE  # 1 Mbps
MIN_BITRATE = 100000  # 500 kbps
DEFAULT_RESOLUTION = (640, 480)

PACKET_MAX = 1300

NAL_TYPE_FU_A = 28
NAL_TYPE_STAP_A = 24

NAL_HEADER_SIZE = 1
FU_A_HEADER_SIZE = 2
LENGTH_FIELD_SIZE = 2
STAP_A_HEADER_SIZE = NAL_HEADER_SIZE + LENGTH_FIELD_SIZE


class H264Encoder:
    def __init__(self, resolution=DEFAULT_RESOLUTION, bitrate=DEFAULT_BITRATE) -> None:
        self.codec = None
        self.__target_bitrate = bitrate
        self.resolution = resolution

    @staticmethod
    def _packetize_fu_a(data: bytes) -> List[bytes]:
        available_size = PACKET_MAX - FU_A_HEADER_SIZE
        payload_size = len(data) - NAL_HEADER_SIZE
        num_packets = math.ceil(payload_size / available_size)
        num_larger_packets = payload_size % num_packets
        package_size = payload_size // num_packets

        f_nri = data[0] & (0x80 | 0x60)  # fni of original header
        nal = data[0] & 0x1F

        fu_indicator = f_nri | NAL_TYPE_FU_A

        fu_header_end = bytes([fu_indicator, nal | 0x40])
        fu_header_middle = bytes([fu_indicator, nal])
        fu_header_start = bytes([fu_indicator, nal | 0x80])
        fu_header = fu_header_start

        packages = []
        offset = NAL_HEADER_SIZE
        while offset < len(data):
            if num_larger_packets > 0:
                num_larger_packets -= 1
                payload = data[offset : offset + package_size + 1]
                offset += package_size + 1
            else:
                payload = data[offset : offset + package_size]
                offset += package_size

            if offset == len(data):
                fu_header = fu_header_end

            packages.append(fu_header + payload)

            fu_header = fu_header_middle
        assert offset == len(data), "incorrect fragment data"

        return packages

    @staticmethod
    def _packetize_stap_a(
        data: bytes, packages_iterator: Iterator[bytes]
    ) -> Tuple[bytes, bytes]:
        counter = 0
        available_size = PACKET_MAX - STAP_A_HEADER_SIZE

        stap_header = NAL_TYPE_STAP_A | (data[0] & 0xE0)

        payload = bytes()
        try:
            nalu = data  # with header
            while len(nalu) <= available_size and counter < 9:
                stap_header |= nalu[0] & 0x80

                nri = nalu[0] & 0x60
                if stap_header & 0x60 < nri:
                    stap_header = stap_header & 0x9F | nri

                available_size -= LENGTH_FIELD_SIZE + len(nalu)
                counter += 1
                payload += pack("!H", len(nalu)) + nalu
                nalu = next(packages_iterator)

            if counter == 0:
                nalu = next(packages_iterator)
        except StopIteration:
            nalu = None

        if counter <= 1:
            return data, nalu
        else:
            return bytes([stap_header]) + payload, nalu

    @staticmethod
    def _split_bitstream(buf: bytes) -> Iterator[bytes]:
        # TODO: write in a more pytonic way,
        # translate from: https://github.com/aizvorski/h264bitstream/blob/master/h264_nal.c#L134
        i = 0
        while True:
            while (buf[i] != 0 or buf[i + 1] != 0 or buf[i + 2] != 0x01) and (
                buf[i] != 0 or buf[i + 1] != 0 or buf[i + 2] != 0 or buf[i + 3] != 0x01
            ):
                i += 1  # skip leading zero
                if i + 4 >= len(buf):
                    return
            if buf[i] != 0 or buf[i + 1] != 0 or buf[i + 2] != 0x01:
                i += 1
            i += 3
            nal_start = i
            while (buf[i] != 0 or buf[i + 1] != 0 or buf[i + 2] != 0) and (
                buf[i] != 0 or buf[i + 1] != 0 or buf[i + 2] != 0x01
            ):
                i += 1
                # FIXME: the next line fails when reading a nal that ends
                # exactly at the end of the data
                if i + 3 >= len(buf):
                    nal_end = len(buf)
                    yield buf[nal_start:nal_end]
                    return  # did not find nal end, stream ended first
            nal_end = i
            yield buf[nal_start:nal_end]

    @classmethod
    def _packetize(cls, packages: Iterator[bytes]) -> List[bytes]:
        packetized_packages = []

        packages_iterator = iter(packages)
        package = next(packages_iterator, None)
        while package is not None:
            if len(package) > PACKET_MAX:
                packetized_packages.extend(cls._packetize_fu_a(package))
                package = next(packages_iterator, None)
            else:
                packetized, package = cls._packetize_stap_a(package, packages_iterator)
                packetized_packages.append(packetized)

        return packetized_packages

    def _encode_frame(
        self, frame, force_keyframe: bool
    ) -> Iterator[bytes]:
        if force_keyframe:
            logger.debug("force keyframe")
            # If a keyframe is forced, it's usually because the browser is confused. 
            # Reset encoder and start over.
            self.codec = None
        if self.codec is None:
            logger.debug("create encoder")
            self.codec = kritter.Encoder(bitrate=self.target_bitrate, resolution=self.resolution)
        if self.codec.bitrate!=self.__target_bitrate:
            self.codec.bitrate = self.__target_bitrate
        if self.codec.resolution!=(frame.shape[1], frame.shape[0]):
            self.codec.resolution = (frame.shape[1], frame.shape[0])
            
        data_to_send = self.codec.encode(cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420))

        if data_to_send:
            yield from self._split_bitstream(data_to_send)

    def encode(
        self, frame, force_keyframe: bool = False
    ) -> List[bytes]:
        packages = self._encode_frame(frame, force_keyframe)
        return self._packetize(packages)

    @property
    def target_bitrate(self) -> int:
        """
        Target bitrate in bits per second.
        """
        return self.__target_bitrate

    @target_bitrate.setter
    def target_bitrate(self, bitrate: int) -> None:
        bitrate = max(MIN_BITRATE, min(bitrate, MAX_BITRATE))
        self.__target_bitrate = bitrate
