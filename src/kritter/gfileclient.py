from logging import raiseExceptions
from .kfileclient import KfileClient
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io

class GfileClient(KfileClient):

    def __init__(self, gcloud):
        drive_creds = gcloud.creds()
        self.drive_client = build('drive', 'v3', credentials=drive_creds)

    '''
    Copys a file of a given path from the vizy to google drive in the requested directory and returns the id
    optional arg specifies wether or not to create the requested dir
    '''
    def copy_to(self, location, destination, create=False):
        dirs = destination.split('/')[1:]
        if not dirs[-1]:
            dirs[-1] = location.split('/')[-1]
        # get the id of the users root directory
        root = self.drive_client.files().get(fileId='root').execute()['id']
        id = root
        parent_id = None
        # follow the detination path
        for dir in dirs[:-1]:
            parent_id = id
            id = self._search_file(self.drive_client,id,dir)
            if(id == None):
                # if create is true, creates the missing directories
                if create:
                    id = self._create_folder(self.drive_client, dir, parent_id)
                else:
                    return(False)
        check = self._search_file(self.drive_client,id,dirs[-1])
        if check:   # something with that name exists
            # if id is a folder:
            if(self.drive_client.files().get(fileId=check).execute()['mimeType'] == 'application/vnd.google-apps.folder'):
                name = location.split('/')[-1]
                id = check
            # if id is a file
            else:
                # delete old file
                rm = '/'
                name = dirs[-1]
                for dir in dirs[:-1]:
                    rm = rm + dir + '/'
                rm = rm + name
                self.delete(rm) 
        else: # file does not exist
            name = dirs[-1]
        # upload the file from 'location' path
        file_meta = {'name': name, 'parents': [id]}
        media = MediaFileUpload(location)
        file = self.drive_client.files().create(body=file_meta, media_body=media, fields='id').execute()
        return(True) 
        
    '''
    Copys a file from the desired location in google drive to the correct path on the vizy
    '''
    def copy_from(self, location, destination):
        dirs = location.split('/')[1:]
        # get the id of the users root directory in google
        root = self.drive_client.files().get(fileId='root').execute()['id']
        id = root
        # follow the location path
        for dir in dirs:
            id = self._search_file(self.drive_client,id,dir)
            if(id == None):
                raise Exception(f"the location '{location}' could not be found in google drive")
        # download file to memory using google drive api
        file_id = id
        request = self.drive_client.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        # save file to drive
        fh.seek(0)
        with open(destination, 'wb') as f:
            f.write(fh.read())
            f.close

    '''
    returns a list of files at a specific path in google drive
    '''
    def list(self, path):
        dirs = path.split('/')[1:]
        # get the id of the users root directory in google
        root = self.drive_client.files().get(fileId='root').execute()['id']
        id = root
        # follow the location path
        for dir in dirs:
            id = self._search_file(self.drive_client,id,dir)
            if(id == None):
                raise Exception(f"the location '{path}' could not be found in google drive")
        parent_id = id

        files = []
        page_token = None
        while True:
            response = self.drive_client.files().list(q=f"parents  in '{parent_id}'",pageToken=page_token).execute()
            for file in response.get('files', []):
                files.append(file.get("name"))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files


    '''
    returns the url in google drive of a file or folder at the provided path
    '''
    def get_url(self, path):
        dirs = path.split('/')[1:]
        # get the id of the users root directory in google
        root = self.drive_client.files().get(fileId='root').execute()['id']
        id = root
        # follow the location path
        for dir in dirs:
            id = self._search_file(self.drive_client,id,dir)
            if(id == None):
                raise Exception(f"the location '{path}' could not be found in google drive")
        if path[-6:]=='.ipynb':
            return f'https://colab.research.google.com/drive/{id}'
        return self.drive_client.files().get(fileId=id,fields='webViewLink').execute()['webViewLink']

    '''
    deletes the folder or file at the path provided
    '''
    def delete(self, path):
        dirs = path.split('/')[1:]
        # get the id of the users root directory in google
        root = self.drive_client.files().get(fileId='root').execute()['id']
        id = root
        # follow the location path
        for dir in dirs:
            id = self._search_file(self.drive_client,id,dir)
            if(id == None):
                raise Exception(f"the location '{path}' could not be found in google drive")
        self.drive_client.files().delete(fileId=id).execute()

    '''
    opens and returns the file similar to the native python open(), for mode: the r option specifies read only
    and the w method allows writing
    '''
    def open(self, path, mode):
        if not (mode == 'r' or mode == 'w'):
            raiseExceptions(f"{mode}: is not a valid mode")
        self.copy_from(path, r'/tmp/tempfile')
        f = open(path, "w")
        _close_orig = f.close
        def _close():
            if(mode == 'w'):
                self.copy_to(r'/tmp/tempfile', r"/test")
            _close_orig()
        f.close = _close
        return f

    '''
    search_file is a helper function that takes the id of the folder you wish to search in 
    as well as the name of what your looking for and returns the id of your target or None
    if the target is not found
    '''
    def _search_file(self, client, parent_id, target_name):
        page_token = None
        response = client.files().list(q=f"parents  in '{parent_id}' and name = '{target_name}'",pageToken=page_token).execute()
        for file in response.get('files', []):
            return(file.get("id"))

    '''
    creates a folder on google drive and returns its id
    '''
    def _create_folder(self, client, folder_name, parent_id):
        body = {
        'name' : folder_name,
        'parents' : [parent_id],
        'mimeType' : 'application/vnd.google-apps.folder'
        }
        folder = client.files().create(body = body).execute()
        return folder['id']
