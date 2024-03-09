# Christian Alameda and Anthony Castillo
import time
import webbrowser
from uuid import uuid4
from threading import Thread
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from controllers.DBconnectionAgent import DBConnectionAgent
import bcrypt

#CLASS IMPORTATION
from controllers.login import Login

from controllers.homepage import Homepage




# import controllers.graphTableGenerator

class MyFlaskApp:
    def __init__(self):
        self.DBconneciton = None
        self._setupDBConnection()
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')
        # self.admin_view = Blueprint('admin_routes',__name__, template_folder='../templates', static_folder='../static')
        
        self.app.secret_key = 'your_secret_key_here'
        
        self.curr_email = ''
        #ROUTECREATING
        #Example: self.app.add_url_rule(route='<route>', name='<name>', function=<function>, OPTIONAL methods=[<typeOfRequest>])
        
        ########
        self.app.add_url_rule('/logged_in', 'logged_in', self.logged_in)
        self.app.add_url_rule('/login', 'login', self.login, methods=['POST', 'GET'])
        self.app.add_url_rule('/logout', 'logout', self.logout, methods=['POST', 'GET'])
        self.app.add_url_rule('/signUp', 'signUp', self.signUp, methods=['POST', 'GET'])
        
        ########
        
        #HOMEPAGE
        self.app.add_url_rule('/', 'index', self.index)
        #ABOUTPAGE
        self.app.add_url_rule('/about', 'about', self.about)
        
        #CLASS_INITIALIZATION
        self.loginClass = Login(self.DBconneciton)
        
        self.homeClass = Homepage()
        
        webbrowser.open("http://127.0.0.1:7777")

    def __del__(self):
        pass   
            
    ################################
    #      Setup DB Connection     #
    ################################
    def _setupDBConnection(self, address="127.0.0.1", port="27017"):
        """Attempts to connect to the MongoDB at the specified address and port. Additionally, creates the medicalAdvisory database if it doesn't exist and setups default collections for master list and preset

        Args:
            address (str, optional): The address for which the MongoDB is located. Defaults to "localhost".
            port (str, optional): The port number for which the MongoDB should be accessed from. Defaults to "27017".
        """
        self.DBconneciton = DBConnectionAgent()
        try:
            if self.DBconneciton.connect(address, port):
                print("Successfully connected to DB at "+"mongodb://"+address+":"+port+"/")
                if self.DBconneciton.useDB('medicalAdvisory'):
                    print('Using the medicalAdvisory database.')
                    tempUUID = str(uuid4())
                    self._checkForUsers(tempUUID)
                    self._checkForUserData(tempUUID)
                    self._checkForSessionKeys(tempUUID)
                else:
                    print('Could not connect to the medicalAdvisory database. Creating new one...')
                    self.DBconneciton.createNewDB('medicalAdvisory')
                    if 'medicalAdvisory' in self.DBconneciton.getDBs():
                        print('Successfully created new database.')
                        if self.DBconneciton.useDB('medicalAdvisory'):
                            print('Using the medicalAdvisory database.')
                            tempUUID = str(uuid4())
                            self._checkForUsers(tempUUID)
                            self._checkForUserData(tempUUID)
                            self._checkForSessionKeys(tempUUID)
                        else:
                            print('Could not connect to the new medicalAdvisory database.')
                    else:
                        print('An Error occured while creating the new medicalAdvisory database.')
            else:
                print("Unable to connect to DB at "+"mongodb://"+address+":"+port+"/")
        except:
            print('There was an error in connecting to MongoDB via ', address, ':', port)
            print('Aborting...')
            self.__del__()

    def _checkForUsers(self, uuid:uuid4):
        """Checks for the existence of the users collection within the database and creates a default one if the collection could not be verified.
        """
        if self.DBconneciton.verifyCollection('users'):
            print('Users collection verified.')
        else:
            print('Error in users, rebuilding the default users.')
            self.DBconneciton.clearDB('users')
            self.DBconneciton.addToDB('users', {'id':uuid, 'username':'admin', 'password':'1234567', 'email':'admin@admin.com', 'creationTime':time.time(),})
            if self.DBconneciton.verifyCollection('users'):
                print('Users rebuilt successfully.')
            else:
                print('An unexpected error occured in the verification of the users.')

    def _checkForUserData(self, uuid:uuid4):
        """Checks for the existence of the userData collection within the userData and creates a default one if the collection could not be verified.
        """
        if self.DBconneciton.verifyCollection('userData'):
            print('userData collection verified.')
        else:
            print('Error in userData, rebuilding the default userData.')
            self.DBconneciton.clearDB('userData')
            self.DBconneciton.addToDB('userData',{'id':uuid,'age':18,'gender':'m','schedules':{},'medications':{},'alternativeTreatment':{},'treatments':{},})
            if self.DBconneciton.verifyCollection('userData'):
                print('userData rebuilt successfully.')
            else:
                print('An unexpected error occured in the verification of the userData.')

    def _checkForSessionKeys(self, uuid:uuid4):
        """Checks for the existence of the sessionKeys collection within the database and creates a default one if the collection could not be verified.
        """
        if self.DBconneciton.verifyCollection('sessionKeys'):
            print('sessionKeys collection verified.')
        else:
            print('Error in sessionKeys, rebuilding the default sessionKeys.')
            self.DBconneciton.clearDB('sessionKeys')
            self.DBconneciton.addToDB('sessionKeys', {'id':uuid, 'token':bcrypt.hashpw('12345'.encode('utf-8'), bcrypt.gensalt())})
            if self.DBconneciton.verifyCollection('sessionKeys'):
                print('sessionKeys rebuilt successfully.')
            else:
                print('An unexpected error occured in the verification of sessionKeys.')

    ################################
    #        AUTH ROUTING          #
    ################################
    #FINISHED
    def signUp(self):
        """_summary_: first page that user will see, if signed in already skip to login, if they haven't fill information and get in database

        Returns:
            html: send them to logged_in.html to back to here so that they can redo their passwords or because they already signed in with those credentials 
        """
        #FOR FIRST TIME LOGGING IN
        message = ''
        # if "email" in session:
        #     self.curr_email = session["email"]
        #     return redirect(url_for("home"))
        if request.method == "POST":
            user = request.form.get("fullname")
            email = request.form.get("email")
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            
            #result needs to be a 
            result = self.register_user(user, email, password1, password2)
            if result == email:
                self.curr_email = email
                return render_template('auth/logged_in.html', email=result)
            else:
                message = result
                return render_template('auth/index.html', message=message)
        return render_template('auth/index.html')
    #FINISHED
    def login(self):
        """_summary_: we check for email and password, first email if email is found then check for email and 
                        password password is done using bcrypt and seeing if password is similar enough

        Returns:
            url or html: depending we send them to homepage or back to the login because they messed up
        """
        message = 'Please login to your account'
        # if "email" in session:
        #     return redirect(url_for("logged_in"))

        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            #Start an insert query
            #don't have user_database will need to to a query and find_user_by_email
            email_found = self.loginClass.find_user_by_email(email) 
            if email_found:
                email_val = email_found['email']
                passwordcheck = email_found['password']

                if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                    session["email"] = email_val
                    self.curr_email = email_val
                    return redirect(url_for('home'))#MAY CHANGE
                else:
                    if "email" in session:
                        return redirect(url_for("home"))#MAY CHANGE
                    message = 'Wrong password'
                    return render_template('auth/login.html', message=message)
            else:
                message = 'Email not found'
                return render_template('auth/login.html', message=message)
        return render_template('auth/login.html', message=message)
    #FINISHED
    def logged_in(self):
        """_summary_: if logged in we just want to send them into their application so go to the homepage.html different then index

        Returns:
            html or url: depending, we will usually send to homepage tho
        """
        if "email" in session:
            email = session["email"]
            self.curr_email = email
            self.addPresetClass.getEmail(self.curr_email)
            #TODO: pass username as context w/ or instead of email.
            return render_template('homepage.html', email=email) #changed from auth/logged_in.html
        else:
            return redirect(url_for("login"))
    #FINISHED
    def register_user(self, user, email, password1, password2):
        """_summary_: for checking whether this user with all this information is in our system as well as inserting them into our system if not

        Args:
            user (str): users chosen username usually first name
            email (str): any strinng we are not checking for valid emails yet
            password1 (str): string of letters numbers and symbols users puts in
            password2 (str): hopefully same letters numbers and symbols might not be we need to check

        Returns:
            str: email that is actually taken from the database so that we know that an insertion occured and that we are now on that document in auth
        """
        # don't have user_database will need to to a query and find_user_by_email as well as name
        user_found = self.loginClass.find_user_by_name(user) 
        email_found = self.loginClass.find_user_by_email(email) 
        
        
        # user_found= {'id': UUID('103d3cac-3fe3-4e19-bfa2-c551456d9d4a'), 'timestamp': 1700092919.792062, 'data': 'Not Yet Implemented'}
        # user_found = (user_found['data'] != 'Not Yet Implemented') #should be False if it is not
        # email_found = (email_found['data'] != 'Not Yet Implemented') #should be False if it is not
        # print('user_found',user_found)
        # print('email_found',email_found)
        
        if user_found:
            return 'There already is a user by that name'
        if email_found:
            return 'This email already exists in the database'
        if password1 != password2:
            return 'Passwords should match'

        hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
        
        user_input = {'name': user, 'email': email, 'id':str(uuid4()), 'password': hashed, 'creationTime':time.time()}
        self.loginClass.insert_user(user_input)
        user_data = self.loginClass.find_user_by_email(email)
        print('user_data|', user_data)
        new_email = user_data['email']
        return new_email
    
    #NOT REALLY USING THIS: #FINISHED
    def logout(self):
        """_summary_: users will have ability to unsign from their account, this really only happens after a user registers

        Returns:
            html or back to home/registration: either shows the signout page or the homepage 
        """
        if "email" in session:
            session.pop("email", None)
            return render_template("auth/signout.html")
        else:
            return redirect(url_for('signUp')) #right now index is home.html but it will be index when done
    
    ################################
    #        NORMAL ROUTING        #
    ################################
    
    #TODO: get numpy in in the query1() so it isn't as slow
    def index(self):
        """_summary_: first thing after being logged in, gives buttons for users to press, this function just renders templates and sends in the email

        Returns:
            html: homepage.html
        """
        # works just fine
        #print(self.viewWebsiteClass.query1())
        self.homeClass.getEmail(self.curr_email)
        
        return render_template('homepage.html')#, userName=self.homeClass.query()) #data=self.viewWebsiteClass.query1())
    
    def about(self):
        """_summary_: just shows an about page that shows what we meant to do with this, as well as describe the makers, and what we believe and hope

        Returns:
            html: aboutpage.html
        """
        return render_template('aboutpage.html') 
    
    

    ################################
    #      TECHNICAL FUNCTIONS     #
    ################################
    def run(self):
        self.app.run(host="0.0.0.0", port=7777)

    def newRequest(self, queryRequest):
        pass

def startFlask():
    newFlask = MyFlaskApp()
    newFlask.run()

# Usage
if __name__ == '__main__':
    my_flask_app = MyFlaskApp()
    my_flask_app.run()
