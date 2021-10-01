import os
import pickle 
import requests
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from .kritter import BASE_DIR

SCOPES = ['https://www.googleapis.com/auth/photoslibrary', 'https://www.googleapis.com/auth/photoslibrary.sharing']
CLIENT_SECRET = os.path.join(BASE_DIR, "client_secret.json")

class Gcloud:

    def __init__(self, auth_file):
        self._creds = None
        self.auth_file = auth_file 

    def _save_creds(self):
        with open(self.auth_file, 'wb') as token:
            pickle.dump(self._creds, token)

    def creds(self):
        if not self.connect():
            return None
        return self._creds  

    def connect(self):
        if self._creds and self._creds.valid:
            return True

        try:
            with open(auth_file, 'rb') as token:
                self._creds = pickle.load(token)
        except:
            return False

        if (not self._creds.valid or self._creds.expired) and _creds.refresh_token:
            self._creds.refresh(Request())
            self._save_creds()

        return self._creds.valid

    def get_url(self, scopes=SCOPES, client_secret=CLIENT_SECRET):
        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secret, scopes=scopes, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        url, state = self.flow.authorization_url(
            # This parameter enables offline access which gives your application
            # an access token and a refresh token for the user's credentials.
            access_type='offline',
            # This parameter enables incremental auth.
            include_granted_scopes='true')

        return url

    def set_code(self, code):
        self.flow.fetch_token(code=code)

        session = self.flow.authorized_session()
        self._creds = session.credentials
        self._save_creds()


