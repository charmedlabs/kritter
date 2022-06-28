
import os
import gspread
import gspread_dataframe as gd
import pandas as pd
from .ktabularclient import KtabularClient


class GtabularClient(KtabularClient):

    def __init__(self, gcloud):
        gcloud = gcloud
        tab_creds = gcloud.creds()
        self.tab_client = gspread.authorize(tab_creds)
        
    '''
    Creates a google sheet with the requested data and returns the sheet
    '''
    def create(self, title, data = pd.DataFrame()):
        find = self.lookup(title)
        if (find != None):
            raise Exception("A Google Sheet with that name already exists")
        sheet = self.tab_client.create(title)
        sh = self.tab_client.open(title) # opens the created worksheet
        worksheet = sh.sheet1 # goes to sheet1
        if not data.empty:
            gd.set_with_dataframe(worksheet, data) # sets the values in the worksheet using a panda data frame 
            worksheet.format('A1:Z1', {'textFormat': {'bold': True}}) # makes headers bold
        return(sheet)
        
    """
    returns the URL of the google sheet and makes the link public share
    """
    def get_url(self,sheet):
        if (sheet == None):
            return "The requested sheet does not exist"
        sheet.share(None, perm_type = 'anyone', role = 'writer', with_link = True)
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/%s" % sheet.id
        return str(spreadsheet_url)

    '''
    looks up the sheet by name and if it exists returns a referance, otherwise returns None
    '''
    def lookup(self, title):
        try:
            found = self.tab_client.open(title)
        except:
            found = None
        return found

    '''
    changes the value of a cell in the requested worksheet
    '''
    def edit_cell(self, sheet, row, col, data):
        worksheet = sheet.sheet1 # goes to sheet1
        worksheet.update_cell(row, col, data)

    '''
    append data adds data to the sheet without overwriting existing data
    '''
    def append_data(self, sheet, data):
        worksheet = sheet.sheet1
        existing = gd.get_as_dataframe(worksheet)
        existing = existing.loc[:, ~existing.columns.str.contains('^Unnamed')] # strips out empty columns
        updated = pd.concat([existing, data], axis=1) # adds the new dataframe to the right
        gd.set_with_dataframe(worksheet, updated)

    '''
    clears all cells in the worksheet
    '''
    def clear(self, sheet):
        worksheet = sheet.sheet1
        worksheet.clear()

    '''
    deletes the requested sheet by name as string
    '''
    def delete(self, title):
        try:
            sheet = self.tab_client.open(title)
        except:
            raise Exception("The Google Sheet: {0} does not exist".format(title))
        self.tab_client.del_spreadsheet(sheet.id)

    '''
    renames the requested sheet 
    '''
    def rename(self, sheet, title):
        sheet.update_title(title)