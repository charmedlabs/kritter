from logging import raiseExceptions
from .kfileclient import KfileClient
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

class GfileClient(KfileClient):

    def __init__(self, gcloud):
        drive_creds = gcloud.creds()
        self.drive_client = build('drive', 'v3', credentials=drive_creds)

    '''
    Copys a file of a given path from the vizy to google drive in the requested directory and returns the id
    '''
    def copy_to(self, location, destination):
        dirs = destination.split('/')
        # get the id of the users root directory
        root = self.drive_client.files().get(fileId='root').execute()['id']
        id = root
        # follow the destination path
        for dir in dirs[1:-1]:
            id = self._search_file(self.drive_client,id,dir)
            if(id == None):
                raise Exception(f"the path '{destination}' could not be found in google drive")
        folder_id = id
        name = dirs[-1]
        # check if the file already exists
        check = self._search_file(self.drive_client,folder_id,name)
        if(check != None):
            raise Exception("the requested file already exists") 
        # upload the file from 'location' path
        file_meta = {'name': name, 'parents': [folder_id]}
        media = MediaFileUpload(location)
        file = self.drive_client.files().create(body=file_meta, media_body=media, fields='id').execute()
        return(file.get("id"))
        

    '''
    Copys a file from the desired location in google drive to the correct path on the vizy
    '''
    def copy_from(self, target, destination):
        pass

    '''
    returns a list of files and their ID's as a dictionary
    '''
    def list(self, path):
        pass

    """
    search_file is a helper function that takes the id of the folder you wish to search in 
    as well as the name of what your looking for and returns the id of your target or -1
    if the target is not found
    """
    def _search_file(self, client, parent_id, target_name):
        try:
            # create drive api client
            files = []
            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = client.files().list(q=f"parents  in '{parent_id}' and name = '{target_name}'",pageToken=page_token).execute()
                for file in response.get('files', []):
                    # Process change
                    #print(F'Found file: {file.get("name")}, {file.get("id")}')
                    return(file.get("id"))
                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
        except:
            return -1

