import os
import pickle
import requests
from httplib2 import Http
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import mimetypes
import base64
from .ktextclient import KtextClient

SUBJECT = "Kritter"


class GtextClient(KtextClient):

    def __init__(self, gcloud):
        super().__init__()
        self.gcloud = gcloud
        self._text = ""

    def text(self, to, text, subject=SUBJECT):
        self.to = to
        self._text += text 
        self.subject = subject 

    def image(self, to, image):
        pass

    def send(self):
        message = self.create_message()
        self._text = ""
        service = build('gmail', 'v1', credentials=self.gcloud.creds(), static_discovery=False)
        message = (service.users().messages().send(userId="me", body=message).execute())
        return message['id']

    def create_message(self):
        message = MIMEText(self._text)
        message['to'] = self.to
        message['from'] = "me"
        message['subject'] = self.subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
