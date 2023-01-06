#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os
import time
import logging
import pickle 
import requests
import socket
import urllib.request
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from .kritter import BASE_DIR
from .kdataclient import KdataClient 
from .gpstoremedia import GPstoreMedia
from .gtextclient import GtextClient
from .gtabularclient import GtabularClient
from .gfileclient import GfileClient

AUTH_FILE = "gcloud.auth"
SCOPES = {"KstoreMedia": ['https://www.googleapis.com/auth/photoslibrary', 'https://www.googleapis.com/auth/photoslibrary.sharing'], "KtextClient": ['https://mail.google.com/'], "KtabularClient": ['https://www.googleapis.com/auth/spreadsheets'], "KfileClient": ['https://www.googleapis.com/auth/drive']}
AUTH_SERVER = "https://auth.vizycam.com"

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "1"

logger = logging.getLogger(__name__)
from .util import set_logger_level
#set_logger_level(logger, logging.DEBUG)

class Gcloud(KdataClient):

    def __init__(self, etcdir):
        self.flow = None
        self.state = None
        super().__init__([k for k, v in SCOPES.items()])
        self._creds = None
        self.auth_file = os.path.join(etcdir, AUTH_FILE) 


    def available_interfaces(self):
        interfaces = self.interfaces.copy()
        creds = self.creds()
        if creds:
            for i in self.interfaces:
                for s in SCOPES[i]:
                    if s not in creds.scopes:
                        interfaces.remove(i)
                        break 
            return interfaces
        return []

    def get_interface(self, interface):
        if interface in self.available_interfaces():
            if interface=='KstoreMedia':
                return GPstoreMedia(self)
            elif interface=='KtextClient':
                return GtextClient(self)
            elif interface=='KtabularClient':
                return GtabularClient(self)
            elif interface=='KfileClient':
                return GfileClient(self)

        # Return None if nothing matches
        return None

    def _save_creds(self):
        with open(self.auth_file, 'wb') as token:
            pickle.dump(self._creds, token)

    def creds(self):
        if not self.connect():
            return None
        return self._creds  

    def remove_creds(self):
        os.rename(self.auth_file, self.auth_file+".bak")
        self._creds = None

    def connect(self):
        if self._creds and self._creds.valid:
            return True

        try:
            with open(self.auth_file, 'rb') as token:
                self._creds = pickle.load(token)
        except:
            return False

        if (not self._creds.valid or self._creds.expired) and self._creds.refresh_token:
            try:
                logger.debug("Refreshing token...")
                self._creds.refresh(Request())
                self._save_creds()
                logger.debug("Success!")
            except Exception as e:
                logger.debug(f"Error refreshing token: {e}")
                return False

        return self._creds.valid

    def get_url(self, client_secret, scopes=SCOPES):
        scopes_list = {i for k, v in scopes.items() for i in v} # set comprehension, no replications

        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secret, scopes=scopes_list, redirect_uri=AUTH_SERVER)
        url, self.state = self.flow.authorization_url(
            # We need these to get a valid refresh token.
            access_type='offline',
            prompt='consent',
            # This parameter enables incremental auth.
            include_granted_scopes='true')

        return url


    def finish_authorization(self):
        if not self.state or not self.flow:
            raise RuntimeError("You need to call get_url() before calling retrieve_code().")
        req = urllib.request.Request(f'{AUTH_SERVER}/poll/?state={self.state}', headers={'User-Agent': 'Mozilla/5.0'})
        try:
            code = urllib.request.urlopen(req, timeout=10).read()
            logger.debug(f"received code: {code}")
            # If we receive b'', it's the same as a timeout (code hasn't arrived) 
            if not code: 
                logger.debug("no code, sleeping...")
                time.sleep(5)
                raise TimeoutError
        except socket.timeout:
            logger.debug("request timed out")
            raise TimeoutError
        code = code.decode('utf-8')
        self.flow.fetch_token(code=code)                  
        self._creds = self.flow.credentials
        logger.debug(f"creds: {self._creds} refresh: {self._creds.refresh_token}")
        self._save_creds()
        return True


'''
# This doesn't work for large files, so we've switched to gdown package for now.
def google_drive_download(id, dest_filename):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    if response.status_code>=400:
        raise RuntimeError("This file is not available.")
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, dest_filename)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, dest_filename):
    CHUNK_SIZE = 32768

    with open(dest_filename, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

'''
