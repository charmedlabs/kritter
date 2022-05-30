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

def send_message(service, to, message):

class GtextClient(KtextClient):

    def __init__(self, gcloud):
        super().__init__()
        self.gcloud = gcloud
        self.callback_receive = None
        self._text = ""

    def text(self, to, text, subject=SUBJECT):
        self.to = to
        self._text += text 
        self.subject = subject 

    def image(self, to, image):
        pass

    def send(self):
        try:
            message = self.create_message()
            service = build('gmail', 'v1', http=self.gcloud.creds().authorize(Http()))
            message = (service.users().messages().send(userId="me", body=message).execute())
            print('Message Id: %s' % message['id'])
        except Exception as e:
            print(f'An error occurred {e}')
        self._text = ""

    def callback_receive(self):
        def wrap_func(func):
            self.callback_receive = func
        return wrap_func

    def create_message(self):
        message = MIMEText(self._text)
        message['to'] = self.to
        message['from'] = "me"
        message['subject'] = self.subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
