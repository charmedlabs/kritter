
import os
import gspread
import gspread_dataframe as gd
import pandas
from .ktabularclient import KtabularClient

class GtabularClient(KtabularClient):

    def __init__(self,gcloud):
        self.gcloud = gcloud
        self.tabScopes = ['https://www.googleapis.com/auth/drive']
        self.tabCreds = self.gcloud.creds()
        self.tabClient = gspread.authorize(self.tabCreds)
        
    '''
    Creates a google sheet with the requested data 
    '''
    def createGS(self,fileName,data):
        self.sheet = self.tabClient.create(fileName)
        sh = self.tabClient.open(fileName) # opens the created worksheet
        worksheet = sh.sheet1 # goes to sheet1
        gd.set_with_dataframe(worksheet, data) # sets the values in the worksheet using a panda data frame 
        worksheet.format('A1:Z1', {'textFormat': {'bold': True}}) # makes headers bold
        
    """
    returns the URL of the google sheet and makes the link public share
    """
    def getURL(self):
        self.sheet.share(None,perm_type = 'anyone', role = 'writer', with_link = True)
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/%s" % self.sheet.id
        return str(spreadsheet_url)