import uuid
import time
class Login:
    def __init__(self, connectionAgent):
        self.connectionAgent = connectionAgent

    #HELPER FUNCTIONS
    def find_user_by_name(self, name): #Should this work?
        """_summary_: find out if name is in dictionary

        Args:
            name (string): should be name of user input

        Returns:
            Bool: true or false depending on if database had it
        """
        temp = self.connectionAgent.requestFromDB('Users', {"name":name})
        return temp

    def find_user_by_email(self, email):
        """_summary_: find out if email is in dictionary

        Args:
            email (str): email that user inputted

        Returns:
            bool: true or false depending on if database has it
        """
        temp = self.connectionAgent.requestFromDB('Users', {"email":email})
        return temp

    def insert_user(self, auth_data):
        """_summary_: simply inserting the data into the database

        Args:
            user_data (dictionary): should be in form of {'name': user, 'email': email, 'id':uuid.uuid4(), 'password': hashed}
        """
        self.connectionAgent.addToDB('Users', {"auth_data":auth_data})
        user_document = {
            'id': auth_data['id'],
            'username':auth_data['name'],
            'email': auth_data['email'],
            'websitesList':[],
            'presets':[]
        }
        self.connectionAgent.addToDB('Users', {"user_document":user_document})