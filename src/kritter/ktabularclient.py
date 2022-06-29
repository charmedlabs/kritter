class KtabularClient:


    def __init__(self):
        pass

    '''
    Creates a google sheet with the requested data and returns the sheet
    '''
    def create(self, title, data = None): # data is a panda data frame
        pass

    '''
    returns the URL of the google sheet and makes the link public share
    '''
    def get_url(self, sheet):
        pass

    '''
    looks up the sheet by name and if it exists returns a referance, otherwise returns None
    '''
    def lookup(self, title):
        pass

    '''
    changes the value of a cell in the requested worksheet
    '''
    def edit_cell(self, sheet, row, col, data):
        pass

    '''
    append data adds data to the sheet without overwriting existing data
    '''
    def append_data(self, sheet, data):
        pass

    '''
    clears all cells in the worksheet
    '''
    def clear(self, sheet):
        pass

    '''
    deletes the requested sheet by name as string
    '''
    def delete(self, sheet):
        pass

    '''
    renames the requested sheet 
    '''
    def rename(self, sheet, title):
        pass