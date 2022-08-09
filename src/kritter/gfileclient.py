from .kfileclient import KfileClient
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

class GfileClient(KfileClient):

    def __init__(self, gcloud):
        drive_creds = gcloud.creds()
        self.drive_client = build('drive', 'v3', credentials=drive_creds)
    '''
    Copys a file of a given path from the vizy to google drive in the requested directory
    '''
    def copy_to(self, target, destination): 
        name = target.split('/')[-1]
        try:
            file_meta = {'name': name}
            media = MediaFileUpload(target)
            file = self.drive_client.files().create(body=file_meta, media_body=media, fields='id').execute()
            return(f'https://drive.google.com/file/d/{file.get("id")}/edit')
        except:
            print('failed to upload to google drive')
            
    '''
    Copys a file from the desired location in google drive to the correct path on the vizy
    '''
    def copy_from(self, target, destination):
        pass

    '''
    returns a list of files and directories at given path in google drive
    '''
    def list(self, path):
        pass

    '''
    returns the url of the file or directory at given path in drive
    '''
    def get_url(slef, path):
        pass

