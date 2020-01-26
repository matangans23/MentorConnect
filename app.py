#!/usr/bin/python3
import os

from flask import Flask
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from flask_table import Table, Col, ButtonCol, DateCol
from flask import render_template, redirect, request, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateTimeField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask_pymongo import PyMongo
from bson import Binary
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from flask import send_file, send_from_directory, safe_join, abort
from flask import current_app
from bson.json_util import dumps
from pymongo import MongoClient
import json
import urllib
from datetime import date
import urllib.request
from bson.json_util import dumps
from queue import PriorityQueue
import database_setup
import suggestions

client = MongoClient('localhost', port=27017)

db = client["mentor_connect"]

collMentors = db["mentors"]
collMentees = db["mentees"]

app = Flask(__name__)
app.config['SECRET_KEY'] = "blah vlah"
print("hey")
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/logindb'
#mongo = PyMongo(app)
#db = mongo.db

Bootstrap(app)

class UploadForm(FlaskForm):
    file = FileField('Upload Profile Picture', validators=[
        FileRequired(),
        FileAllowed(['.jpg', '.png'], 'File extension must be ".jpg" or ".png"')
    ])
    submit = SubmitField('Submit')
    
class User(UserMixin):

    #initialize use with email and name. Initialized _id and password_hash to NOne
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self._id = None
        self.password_hash = None


class LoginForm(FlaskForm):
    email_or_user = StringField('Brown ID', validators=[DataRequired()])
    #password = PasswordField('Password', validators=[DataRequired()])
    mentee = RadioField('Mentor or Mentee?', choices = [("Mentor", "Mentor"), ("Mentee", "Mentee")])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    brown_id = StringField('Brown ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    concentration =  StringField('Concentration', validators=[DataRequired()])
    courses_taken = StringField('Courses Taken', validators=[DataRequired()])
    planned = StringField('Courses Planned')
    helpp = SelectMultipleField(u'Areas of Help/Advising', choices=[('Concentration Choice/Declaration',
     'Concentration Choice/Declaration'), ('Course Plan', 'Course Plan'), ('Internship/Career Advice', 'Internship/Career Advice'),
    ('Extracurriculars', 'Extracurriculars'),('Study Tips', 'Study Tips')])
    #helpp = RadioField('Areas of Help', choices = [('Concentration Choice/Declaration', 'Concentration Choice/Declaration'),('Internship/Career Advice', 'Internship/Career Advice'), ('Course Plan', 'Course Plan'), ('Extracurriculars', 'Extracurriculars'), ('Study Tips', 'Study Tips')], validators=[DataRequired()])
    mentee = RadioField('Mentor or Mentee?', choices = [("Mentor", "Mentor"), ("Mentee", "Mentee")])
    submit = SubmitField('Register')
# class InformationForm(FlaskForm):
#     name = StringField('Name',validators=[DataRequired()]), 
#     year = StringField('Year', validators=[DataRequired()])
#     concentration = StringField('Concentration',validators=[DataRequired()])
#     courses_taken = String
#     confirm = PasswordField('Repeat Password')
#     remember_me = BooleanField('Keep me logged in')
#     submit = SubmitField('Register')


login_manager = LoginManager(app)
login_manager.login_view = 'login' # route or function where login occurs...


@app.route('/')
@login_required
def index():
    return redirect(url_for('/login'))

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
global mentor
global mentee
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    user = None
    global user_info
    user_info = None
    global mentor1
    mentor1 = None
    form = LoginForm()

    if form.validate_on_submit():
        if form.mentee.data == "Mentor":
            print("yee")
            if collMentors.find({"brown_id" : form.email_or_user.data}).count() > 0:
                user_info = collMentors.find({"brown_id" : form.email_or_user.data})[0]
                mentor1 = "Mentor"
            else:
                flash('invalid username or password.')
        else:
            if collMentees.find({"brown_id" : form.email_or_user.data}).count() > 0:
                user_info = collMentees.find({"brown_id" : form.email_or_user.data})[0]
                mentor1 = "Mentee"
            else:
                flash('invalid username or password.')
        print(user_info)
        if user_info is not None: #and (user == mentee or user== mentor):# user.verify_password(form.password.data):
            return redirect('/profile')

    return render_template('user_login.html', form=form)



@app.route('/register', methods=['GET','POST'])
def register():
    global user_info
    user_info = None
    global mentor1
    mentor1 = None
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        brown_id = form.brown_id.data
        name = form.name.data
        year = form.year.data
        concentration = form.concentration.data
        courses_taken = form.courses_taken.data
        courses_taken = courses_taken.split(", ")
        planned = form.planned.data
        planned = planned.split(", ")
        helpp = form.helpp.data
        mentor1 = form.mentee.data
        temp_id_dictionary = {}
        if mentor1 == "Mentor":
            database_setup.addMentor(email, brown_id, name, year, concentration, courses_taken, helpp)
            temp_id_dictionary = collMentors.find({"brown_id": brown_id})[0]
        else:
            database_setup.addMentee(email, brown_id, name, year, concentration, courses_taken, planned, helpp)
            temp_id_dictionary = collMentees.find({"brown_id": brown_id})[0]
        user_info = dict(temp_id_dictionary)

        print(user_info)
        print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
        return redirect('/profile')
    else:
        return render_template('new_user.html',form = form)

    # return redirect(url_for('register'))

@app.route('/profile', methods=['GET','POST'])
def add_information():
    # if mentor is not None:
    #     return render_template('current_user_profile.html', brown_id = mentor['brown_id'], year = mentor['year'], concentration = mentor['concentration'],   name=mentor['name'], courses_taken = mentor['courses_taken'], planned = mentor['planned_courses'], helpp = mentor['areas_of_help'])
    # if mentee is not None:
    #     return render_template('current_user_profile.html', brown_id = mentor['brown_id'], year = mentor['year'], concentration = mentor['concentration'],   name=mentor['name'], courses_taken = mentor['courses_taken'], planned = mentor['planned_courses'], helpp = mentor['areas_of_help'])
    print(user_info)
    print(request.form)
    documents()
    print("YERRRRRRRRRRRRR")
    print(mentor1)
    if mentor1 == "Mentor":
        matched = None
        counter = 0
        for id1 in user_info['matched']:
            if counter == 0:
                matched = []
            matched.append(collMentees.find( {'brown_id' : id1})[0])
        return render_template('profile.html', brown_id = user_info['brown_id'], year = user_info['year'], concentration = user_info['concentration'],   name=user_info['name'], courses_taken = user_info['courses_taken'], planned = None, helpp = user_info['areas_of_help'], form=form1, matched=matched)
    else:
        matched = None
        counter = 0
        for id1 in user_info['matched']:
            if counter == 0:
                matched = []
            matched.append(collMentors.find( {'brown_id' : id1})[0])
        return render_template('profile.html', brown_id = user_info['brown_id'], year = user_info['year'], concentration = user_info['concentration'],   name=user_info['name'], courses_taken = user_info['courses_taken'], planned = user_info['planned_courses'], helpp = user_info['areas_of_help'], form=form1, matched=matched)

def documents():
    global form1
    form1 = UploadForm(method='POST')
    multiselect = request.form.getlist('mymultiselect')
    user_id = session.get('user_id')
    with open('file.jpg', 'wb+') as f:
       cursor = db.documents.find()
       k = 0
       for i in cursor:
           if k == 2:
               f.write(i['file'])
           k += 1
    if form1.submit.data and form1.validate_on_submit():
        print(form.doc_type.data)
        filename = secure_filename(form1.file.data.filename)
        doc_type = form1.doc_type.data
        bytes_file = form1.file.data.read()
        curr_dir = os.getcwd()
        dir_path = curr_dir + "/static/client/" + user_id + "/" # appended / at the end of str
        print(dir_path)
        if not os.path.exists(dir_path):
            # do not need to change dir_path here
            os.mkdir(dir_path)
        with open(dir_path + doc_type +'.jpg', 'wb+') as f:
            f.write(bytearray(bytes_file))

        new_doc_for_mongo = {
            'user_id' : ObjectId(user_id),
            'filename' : filename,
            'doc_type' : doc_type,
            'file' : Binary(bytes_file)
            }
        db.documents.remove({'$and' : [{'user_id' : ObjectId(user_id)},{'doc_type' : doc_type}]})
        db.documents.insert_one(new_doc_for_mongo)
        form1.file.data = ''
        print('HAYYYYYYYYYYYYYYYYYYYYY')
        

        #return redirect(url_for('documents'))
    documents = list(db.documents.find({'user_id' : ObjectId(user_id)}))

    # return render_template('documents.html', form=form, documents=documents)

@app.route("/get-pdf/<pdf_id>")
@login_required
def get_pdf(pdf_id):
    user_id = session.get('user_id')
    filename = pdf_id
    # host_dir needs to change for each host. this will need to be updated for our server and for each local deployment case
    host_dir = os.getcwd()
    directory = host_dir + '/static/client/' + user_id + '/'

    try:
        return send_from_directory(directory=directory, filename=filename, as_attachment=True, mimetype='application/pdf')
    except FileNotFoundError:
        abort(404)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('login'))

##### Hossam's Stuff
list_of_docs = []
@app.route('/search', methods=['POST', 'GET']) #TODO
def main_page():
    if mentor1 == "Mentee":
        names = set()
        concentrations = set()
        courses = set()
        helped = set()
        for docs in collMentors.find():
            names.add(docs['name'])
            concentrations.add(docs['concentration'])
            for course in docs['courses_taken']:
                courses.add(course)
            for help in docs['areas_of_help']:
                helped.add(help)
        return render_template('filter_page.html', names=names, concentrations=concentrations, courses = courses, helped = helped, list_of_docs = list_of_docs)
    else:
        names = set()
        concentrations = set()
        courses = set()
        helped = set()
        for docs in collMentees.find():
            names.add(docs['name'])
            concentrations.add(docs['concentration'])
            for course in docs['courses_taken']:
                courses.add(course)
            for help in docs['areas_of_help']:
                helped.add(help)
        return render_template('filter_page.html', names=names, concentrations=concentrations, courses = courses, helped = helped, list_of_docs = list_of_docs)
    #  TODO: Handle serving the main page and AddForm submission here.

@app.route("/query", methods=['POST']) #TODO
def remove_todo():
    print("Hello")
    queryDict = {}
    if request.form.get('name') is not '':
        queryDict['name'] = request.form.get('name')
    if request.form.get('concentration') is not '':
        queryDict['concentration'] = request.form.get('concentration')
    if request.form.get('multi') is not "None":
        classes_list = request.form.get('multi')
    if request.form.get('help') is not "None":
        help = request.form.get('help')
    q = PriorityQueue()
    print(queryDict)
    for mentors in collMentors.find(queryDict):
        score = 0
        if classes_list:
            for classes in mentors["courses"]:
                if classes in classes_list:
                    score += 2
        if help:
            for helps in mentors['areas_of_help']:
                if helps in help:
                    score += 1
        q.put((score, mentors["brown_id"]))
    listoftop = []
    counter = 0
    while not q.empty():
        listoftop.append(q.get())
        counter += 1
        if counter == 6:
            break
    for id_s in listoftop:
        list_of_docs.append(collMentors.find({ "brown_id" : id_s[1] })[0])
    return redirect("/search")

@app.route('/best')
def top():
    if mentor1 == "Mentee":
        sugg = suggestions.suggest(user_info["brown_id"])
        return render_template("top_res.html", list=sugg)
    else:
        lis = user_info['matched']
        interested_mentees = []
        for id1 in lis:
            interested_mentees.append(collMentees.find( {'brown_id' : id1})[0])
        return render_template("top_res.html", list=interested_mentees)
@app.route('/interested', methods=["POST"])
def interested():
    if mentor1 == "Mentee":
        lis = request.form.getlist('checkbox')
        for x in lis:
            collMentors.update({'brown_id': x}, {'$push': {'matched': user_info['brown_id']}})
    if mentor1 == "Mentor":
        lis = request.form.getlist('checkbox')
        for x in lis:
            collMentees.update({'brown_id': x}, {'$push': {'matched': user_info['brown_id']}})
    return redirect("/profile")
app.run()
