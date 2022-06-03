import os
import pickle
import requests
from httplib2 import Http
from googleapiclient.discovery import build
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2
import mimetypes
import base64
from .ktextclient import KtextClient

SUBJECT = "Kritter"


class GtextClient(KtextClient):

    def __init__(self, gcloud):
        super().__init__()
        self.gcloud = gcloud
        self.reset()

    def reset(self):
        self._text = ""
        self._images = []

    def text(self, to, text, subject=SUBJECT):
        self.to = to
        self._text += text 
        self.subject = subject 

    def image(self, to, image):
        self.to = to
        if isinstance(image, str):
            if os.path.exists(image):
                with open(image, 'rb') as image:
                    self._images.append(image.read())
            elif image.lower().startswith("http"):
                self._images.append(image)
            else:
                raise RuntimeError(f"Unknown image type: {image}")
        else: # assume it's a numpy array
            try:
                self._images.append(cv2.imencode('.jpg', image)[1].tobytes())
            except Exception as e:
                raise RuntimeError(f"Error processing image array: {e}")


    def send(self):
        message = self.create_message()
        self.reset()
        service = build('gmail', 'v1', credentials=self.gcloud.creds(), static_discovery=False)
        message = (service.users().messages().send(userId="me", body=message).execute())
        return message['id']

    def create_message(self):
        message = MIMEMultipart('related')
        message['To'] = self.to
        message['From'] = "me"
        message['Subject'] = self.subject
        message.preamble = 'This is a multi-part message in MIME format.'
        text = f'<pre>{self._text}</pre>'
        embeds = []
        for i, image in enumerate(self._images):
            if isinstance(image, str):
                text += f'<br><img src="{image}">'
            else:
                text += f'<br><img src="cid:image{i}">'
                embed = MIMEImage(image)
                embed.add_header('Content-ID', f'<image{i}>')
                embeds.append(embed)

        message.attach(MIMEText(text, 'html'))
        for e in embeds:
            message.attach(e)

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
