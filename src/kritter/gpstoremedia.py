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
import json
import pickle
import requests
from .kstoremedia import KstoreMedia
from googleapiclient.discovery import build


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


    def store_image_file(self, filename, album="", desc="", data={}):
        service = build('photoslibrary', 'v1', credentials=self.gcloud.creds(), static_discovery=False)

        album_id = None
        if album:
            try:
                albums = service.sharedAlbums().list().execute()
                albums = albums['sharedAlbums']
                for a in albums:
                    if 'title' in a and a['title']==album:
                        album_id = a['id']
                        break
            except:
                pass
            if album_id is None:
                try:
                    albums = service.albums().list().execute()
                    albums = albums['albums']
                    for a in albums:
                        if 'title' in a and a['title']==album:
                            album_id = a['id']
                            break
                except:
                    pass
            # new album
            if album_id==None:
                try:
                    response = service.albums().create(body={'album': {'title': album}}).execute()
                    album_id = response['id']
                except:
                    pass

        # Call the Drive v3 API
        upload_token = self._post_gphoto(filename)
        # If we want to save data with picture instead of just a description string, 
        # turn description string into a json string and add desc (if needed).
        if data:
            if desc:
                data['desc'] = desc
            desc = json.dumps(data)
        body = {
            'album_id': album_id, 
            'newMediaItems': [
                {
                    "description": desc,
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
        return results['newMediaItemResults'][0]['mediaItem']['productUrl']

    def store_video_file(self, filename, album="", desc="", data={}):
        # Google Photos accepts videos through the same API path as images.
        return self.store_image_file(filename, album, desc)

    def get_share_url(self, album):
        service = build('photoslibrary', 'v1', credentials=self.gcloud.creds(), static_discovery=False)
        album_id = None
        try:
            albums = service.albums().list().execute()
            albums = albums['albums']
            for a in albums:
                if 'title' in a and a['title'] == album:
                    album_id = a['id']
                    request_body = {
                        'sharedAlbumOptions': {
                            'isCollaborative': True,
                            'isCommentable': True
                        }  
                    }
                    try: # try sharing album
                        response = service.albums().share(albumId=album_id,body=request_body).execute()
                        return response['shareInfo']['shareableUrl']
                    except:
                        # if album is already shared, just get url
                        return service.albums().get(albumId = album_id).execute()['productUrl']
        # if album by that name not found return none
        except: 
            return None
