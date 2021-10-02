import os
import pickle
import requests
from .kstoremedia import KstoreMedia
from googleapiclient.discovery import build
from kritter import Gcloud


class GPstoreMedia(KstoreMedia):

    def __init__(self, gcloud):
        super().__init__()
        self.gcloud = gcloud

    def _post_gphoto(self, filename):
        f = open(filename, 'rb').read();

        url = 'https://photoslibrary.googleapis.com/v1/uploads'
        headers = {
            'Authorization': "Bearer " + self.gcloud.creds().token,
            'Content-Type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': os.path.basename(filename),
            'X-Goog-Upload-Protocol': "raw",
        }

        r = requests.post(url, data=f, headers=headers)
        return r.content


    def save(self, filename, album=""):
        service = build('photoslibrary', 'v1', credentials=self.gcloud.creds(), static_discovery=False)

        album_id = None
        if album!="":
            if False: # shared album -- not sure if this is really needed...
                albums = service.sharedAlbums().list().execute()
                albums = albums['sharedAlbums']
                for a in albums:
                    if a['title']==album:
                        album_id = a['id']
                        break
            else: # try to find in list of albums
                albums = service.albums().list().execute()
                albums = albums['albums']
                for a in albums:
                    if a['title']==album:
                        album_id = a['id']
                        break
            # new album
            if album_id==None:
                response = service.albums().create(body={'album': {'title': album}}).execute()
                album_id = response['id']

        # Call the Drive v3 API
        upload_token = self._post_gphoto(filename)
        body = {
                    'album_id': album_id, 
                    'newMediaItems': [
                        {
                            #"description": "test video",
                            "simpleMediaItem": 
                            {
                                "uploadToken": upload_token.decode('UTF-8')
                            }
                        }
                    ]
                }
        # remove entry if no album
        if album_id==None:
            body.pop('album_id')

        results = service.mediaItems().batchCreate(body=body).execute()
        result = results['newMediaItemResults'][0]['status']['message']


        success = result=='Success' or result=='OK'
        if not success:
            print('*** Error:', result)
        return success
