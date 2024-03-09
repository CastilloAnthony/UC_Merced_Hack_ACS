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
    
    def query(self):
        
        # print(self.curr_email) 
        #ca
        
        grabAuthThroughEmail = {
            'id': uuid.uuid4(),
            'request_type': 'request',
            'column': 'auth',
            'query': {"email":self.curr_email}
        }
        temp = requestData(grabAuthThroughEmail, self.__requestQ, self.__dataQ)
        #temp = 
        # {'id': UUID('18938276-4528-4865-922d-d6f0673adab9'), 
        # 'timestamp': 1700172860.5806377, 
        # 'data': {'_id': ObjectId('65565326c3a6e4404edd07d8'), 
        # 'name': 'ca', 
        # 'email': 'ca', 
        # 'id': 'ee76936a-d4b0-4050-986d-b4a71041138b', 
        # 'password': b'$2b$12$YL/oMnZx4cbALMWonGfQ4.WruGxhp/N/RPd.f3i.rg7aZxyEkW8Qi'}
        # }
        return temp
        
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