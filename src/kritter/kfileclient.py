class KfileClient:

    def __init__(self):
        pass
    '''
    Copys a file of a given path from the vizy to google drive in the requested directory and returns the id
    optional arg specifies wether or not to create the requested dir
    '''
    def copy_to(self, location, destination, create=False, status_func=None): 
        pass

    '''
    Copys a file from the desired location in google drive to the correct path on the vizy
    '''
    def copy_from(self, location, destination, status_func=None):
        pass

    '''
    returns a list of files at a specific path in google drive
    '''
    def list(self, path):
        pass

    '''
    returns the url in google drive of a file or folder at the provided path
    '''
    def get_url(self, path):
        pass

    '''
    deletes the folder or file at the path provided
    '''
    def delete(self, path):
        pass

    '''
    opens and returns the file similar to the native python open(), for mode: the r option specifies read only
    and the w method allows writing
    '''
    def open(self, path, mode):
        pass

    '''
    closes the already opened file and pushes any updates to drive
    '''
    def close(self, path):
        pass