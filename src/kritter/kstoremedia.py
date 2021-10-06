import cv2

TEMP_FILENAME = "/tmp/image.jpg"

class KstoreMedia:

	def __init__(self):
		pass

	def store_image_array(self, array, album="", desc=""):
		cv2.imwrite(TEMP_FILENAME, array, [cv2.IMWRITE_JPEG_QUALITY, 100])
		return self.store_image_file(TEMP_FILENAME, album, desc)

	def store_image_file(self, filename, album="", desc=""):
		pass

	def store_video_stream(self, stream, fps=30, album="", desc=""):
		pass

	def store_video_file(self, filename, fps=30, album="", desc=""):
		pass
