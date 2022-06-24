
import os
import gspread
import gspread_dataframe as gd
import pandas
from .ktabularclient import KtabularClient


class GtabularClient(KtabularClient):

    def __init__(self, gcloud):
        self.gcloud = gcloud
        self.tab_creds = self.gcloud.creds()
        self.tab_client = gspread.authorize(self.tabCreds)
        
    '''
    Creates a google sheet with the requested data 
    '''
    def create(self, fileName, data):
        self.sheet = self.tab_client.create(fileName)
        sh = self.tab_client.open(fileName) # opens the created worksheet
        worksheet = sh.sheet1 # goes to sheet1
        gd.set_with_dataframe(worksheet, data) # sets the values in the worksheet using a panda data frame 
        worksheet.format('A1:Z1', {'textFormat': {'bold': True}}) # makes headers bold
        return(self.sheet)
        
    """
    returns the URL of the google sheet and makes the link public share
    """
    def getURL(self):
        self.sheet.share(None,perm_type = 'anyone', role = 'writer', with_link = True)
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/%s" % self.sheet.id
        return str(spreadsheet_url)