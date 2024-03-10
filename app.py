# Christian Alameda and Anthony Castillo
import time
import webbrowser
from uuid import uuid4
from threading import Thread
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from controllers.DBconnectionAgent import DBConnectionAgent
import bcrypt

class MyFlaskApp:
    def __init__(self):
        self.DBconneciton = None
        self._setupDBConnection()
        self.app = Flask(__name__, template_folder='./templates', static_folder='./static')
        # self.admin_view = Blueprint('admin_routes',__name__, template_folder='../templates', static_folder='../static')
        
        self.app.secret_key = str(uuid4)#'your_secret_key_here'
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
        ########
        
        self.app.add_url_rule('/search', 'search', self.search, methods=['POST', 'GET'])
        self.app.add_url_rule('/searchAnswer', 'searchAnswer', self.searchAnswer, methods=['POST', 'GET'])
        self.app.add_url_rule('/profile', 'profile', self.profile, methods=['POST', 'GET'])
        
        
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
            self.DBconneciton.addToDB('users', {'id':uuid, 'username':'admin', 'email':'admin@admin.com', 'password':bcrypt.hashpw('12345'.encode('utf-8'), bcrypt.gensalt()), 'creationTime':time.time(),})
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

    ################################
    #        AUTH ROUTING          #
    ################################
    def signUp(self):
        """_summary_: first page that user will see, if signed in already skip to login, if they haven't fill information and get in database

        Returns:
            html: send them to logged_in.html to back to here so that they can redo their passwords or because they already signed in with those credentials 
        """
        #FOR FIRST TIME LOGGING IN
        message = ''
        if "id" in session:
            return redirect(url_for("logged_in"))
        if request.method == "POST":
            user = request.form.get("fullname")
            email = request.form.get("email")
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            result = self.register_user(user, email, password1, password2)
            if result == True:
                return render_template('auth/logged_in.html', userName=self.DBconneciton.requestFromDB('users', {'id':session['id']})['username'])
            else:
                return render_template('auth/index.html', message=result)
        return render_template('auth/index.html')

    def login(self):
        """_summary_: we check for email and password, first email if email is found then check for email and 
                        password password is done using bcrypt and seeing if password is similar enough

        Returns:
            url or html: depending we send them to homepage or back to the login because they messed up
        """
        message = 'Please login to your account'
        if "id" in session:
            return redirect(url_for("logged_in"))

        if request.method == "POST":
            user_input = request.form.get("email")
            password = request.form.get("password")
            email_found = self.DBconneciton.requestFromDB('users', {'email':user_input})
            username_found = self.DBconneciton.requestFromDB('users', {'username':user_input})
            # print(user_input, password, email_found, username_found)
            if email_found:
                email_val = email_found['email']
                passwordcheck = email_found['password']
                if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                    session['id'] =  email_found['id']
                    return redirect(url_for('index'))#MAY CHANGE
                else:
                    message = 'Wrong password'
                    return render_template('auth/login.html', message=message)
            elif username_found:
                username_val = username_found['username']
                passwordcheck = username_found['password']
                if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                    session['id'] =  username_found['id']
                    return redirect(url_for('index'))#MAY CHANGE
                else:
                    message = 'Wrong password'
                    return render_template('auth/login.html', message=message)
            else:
                message = 'Email not found'
                return render_template('auth/login.html', message=message)
        return render_template('auth/login.html', message=message)

    def logged_in(self):
        """_summary_: if logged in we just want to send them into their application so go to the homepage.html different then index

        Returns:
            html or url: depending, we will usually send to homepage tho
        """
        if "id" in session:
            #TODO: pass username as context w/ or instead of email.
            return render_template('homepage.html', userName=self.DBconneciton.requestFromDB('users', {'id':session['id']})['username']) #changed from auth/logged_in.html
        else:
            return redirect(url_for("homepage.html"))
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
        user_found = self.DBconneciton.requestFromDB('users', {'username':user})
        email_found = self.DBconneciton.requestFromDB('users', {'email':email})
        
        if user_found:
            return 'There already is a user by that name'
        if email_found:
            return 'This email already exists in the database'
        if password1 != password2:
            return 'Passwords should match'

        hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
        tempID = str(uuid4())
        user_input = {'id':tempID, 'username': user, 'email': email,  'password': hashed, 'creationTime':time.time()}
        session['id'] = tempID
        temp = self.DBconneciton.addToDB('users', user_input)
        if temp != False:
            print('Added '+user+' to the database with data: ', str(user_input))
            return True
        else:
            print('Could not add '+user+' to the database with data: ', str(user_input))
            return 'An error occurred'
    
    #NOT REALLY USING THIS: #FINISHED
    def logout(self):
        """_summary_: users will have ability to unsign from their account, this really only happens after a user registers

        Returns:
            html or back to home/registration: either shows the signout page or the homepage 
        """
        if 'id' in session:
            session.pop("id", None)
            return render_template("auth/signout.html")
        else:
            return redirect(url_for('index')) #right now index is home.html but it will be index when done
    
    ################################
    #        NORMAL ROUTING        #
    ################################
    
    #TODO: get numpy in in the query1() so it isn't as slow
    def index(self):
        """_summary_: first thing after being logged in, gives buttons for users to press, this function just renders templates and sends in the email

        Returns:
            html: homepage.html
        """
        if 'id' in session:
            return render_template('homepage.html', userName=self.DBconneciton.requestFromDB('users', {'id':session['id']})['username']) #data=self.viewWebsiteClass.query1())
        else:
            return render_template('homepage.html')

    def about(self):
        """_summary_: just shows an about page that shows what we meant to do with this, as well as describe the makers, and what we believe and hope

        Returns:
            html: aboutpage.html
        """
        return render_template('aboutpage.html') 
    
    
    def search(self):
        return render_template('search.html')

    def searchAnswer(self):
        return render_template('searchAnswer.html')

    def profile(self):
        if 'id' in session:
            return render_template('profile.html', userName=self.DBconneciton.requestFromDB('users', {'id':session['id']})['username'])
        else:
            return redirect('/login')

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
    newFlask = MyFlaskApp()
    newFlask.run()