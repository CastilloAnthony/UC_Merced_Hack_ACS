# CHRISTIAN
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify

import uuid
import time
#pip install bcrypt
import bcrypt
from multiprocessing import Queue

#CLASS IMPORTATION
from controllers.login import Login

from controllers.homepage import Homepage


import webbrowser

# import controllers.graphTableGenerator

class MyFlaskApp:
    def __init__(self, requestQ:Queue, dataQ:Queue):
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')
        # self.admin_view = Blueprint('admin_routes',__name__, template_folder='../templates', static_folder='../static')
        
        self.app.secret_key = 'your_secret_key_here'
        
        self.app.requestQ = requestQ
        self.app.dataQ = dataQ
        
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
        self.loginClass = Login()
        
        self.homeClass = Homepage()
        
        webbrowser.open("http://127.0.0.1:7777")
             
            
        
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
        
        user_input = {'name': user, 'email': email, 'id':str(uuid.uuid4()), 'password': hashed, 'creationTime':time.time()}
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
        
        return render_template('homepage.html', userName=self.homeClass.query()) #data=self.viewWebsiteClass.query1())
    
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

def startFlask(requestQ, dataQ):
    newFlask = MyFlaskApp(requestQ, dataQ)
    newFlask.run()

# Usage
if __name__ == '__main__':
    request_queue = Queue()
    data_queue = Queue()
    my_flask_app = MyFlaskApp(request_queue, data_queue)
    my_flask_app.run()
