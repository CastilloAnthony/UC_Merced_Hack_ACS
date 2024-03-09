#CHRISTIAN
import uuid
import time
import requests
from flask import Flask, render_template, request
from controllers.DBconnectionAgent import DBConnectionAgent


class Search(): # Controller
    def __init__(self, connectionAgent:DBConnectionAgent):
        self.connectionAgent = connectionAgent
        
    def __del__(self):
        pass
    
    def searchAnswer(self):
        url = request.form['url']
        
    def addWebsite(self):
        """_summary_: inputting the url into the masterlist collection as well as inputing the url into the users collection
        """
        identifier = self.query()['data']['id']
        url = request.form['url']
        oneWebsite = {
            'id': uuid.uuid4(),
            'request_type': 'insert',
            'column': 'masterList',
            'query': url
        }
        self.__requestQ.put(oneWebsite)
        oneWebsite = {
            'id': uuid.uuid4(),
            'request_type': 'update',
            'column': 'users', 
            #filter_criteria = {"_id": ObjectId("your-document-id")}
            'query': {'id': identifier},#GOOD
            'changeTo':  {'websitesList':url} #GOOD?
        }
        self.__requestQ.put(oneWebsite)
            
#end AddPreset