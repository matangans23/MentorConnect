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
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateTimeField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask_table import Table, Col
from flask_pymongo import PyMongo
from bson import Binary
from bson.objectid import ObjectId
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from flask import send_file, send_from_directory, safe_join, abort
from flask import current_app

import database_setup

app = Flask(__name__)
app.config['SECRET_KEY'] = "blah vlah"
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/logindb'
#mongo = PyMongo(app)
#db = mongo.db

Bootstrap(app)

class User(UserMixin):

    #initialize use with email and name. Initialized _id and password_hash to NOne
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self._id = None
        self.password_hash = None
	
	
class LoginForm(FlaskForm):
    email_or_user = StringField('Email or username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):  
    name = StringField('Name', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    concentration =  StringField('Concentration', validators=[DataRequired()])
    courses_taken = StringField('Courses Taken', validators=[DataRequired()])
    planned = StringField('Courses Planned', validators=[DataRequired()])
    helpp = StringField('Help', validators=[DataRequired()])
    submit = SubmitField('Register')
# class InformationForm(FlaskForm):
#     name = StringField('Name',validators=[DataRequired()])
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
    return redirect(url_for('internships'))

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query(form.email_or_user.data)

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('internships'))
        flash('invalid username or password.')

    return render_template('user_login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        year = form.year.data
        concentration = form.concentration.data
        courses_taken = form.courses_taken.data
        courses_taken = courses_taken.split(", ")
        planned = form.planned.data
        planned = planned.split(", ")
        helpp = form.helpp.data
        helpp = helpp.split(", ")
        user.password = form.password.data # this calls the hash setter
        database_setup.addMentee(name, year, concentration, courses_taken, planned, helpp)
    return render_template('register.html',form = request.form)
    # return redirect(url_for('register'))


@app.route('/profile', methods=['POST'])
def add_information():
	if request.method == 'POST': 
		name = request.form.get["name"]
		year = request.form['year']
		concentration = request.form['concentration']
		courses_taken = request.form['courses_taken']
		courses_taken = list(courses_taken)
		planned  = request.form['planned']
		planned = list(planned)
		helpp = request.form['help']
		helpp = list(helpp)
		database_setup.addMentee(name, year, concentration, courses_taken, planned, helpp)
		print(type(request.form))
		print(request.form)
		return render_template('profile.html',form = request.form)
	return render_template('profile.html')
# @app.route('/profile', methods=['GET','POST'])
# @login_required
# def load_user_info():

class UploadForm(FlaskForm):
    file = FileField('Upload PDF Document', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'File extension must be ".pdf"')
    ])
    doc_type = RadioField('Document Type',
                    default='resume',
                    choices=[('resume','resume (most recent)'),
                    ('cover-letter', 'cover letter (generic)'),
                    ('transcript','transcript (most recent)')],
                    validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/documents', methods=['GET', 'POST'])
@login_required
def documents():
    form = UploadForm(method='POST')
    user_id = session.get('user_id')
#    with open('file.pdf', 'wb+') as f:
#        cursor = db.documents.find()
#        k = 0
#        for i in cursor:
#            if k == 2:
#                f.write(i['file'])
#            k += 1
    if form.submit.data and form.validate_on_submit():
        print(form.doc_type.data)
        filename = secure_filename(form.file.data.filename)
        doc_type = form.doc_type.data
        bytes_file = form.file.data.read()
        curr_dir = os.getcwd()
        dir_path = curr_dir + "/static/client/" + user_id + "/" # appended / at the end of str
        if not os.path.exists(dir_path):
            # do not need to change dir_path here 
            os.mkdir(dir_path)
        with open(dir_path + doc_type +'.pdf', 'wb+') as f:
            f.write(bytearray(bytes_file))

        new_doc_for_mongo = {
            'user_id' : ObjectId(user_id),
            'filename' : filename,
            'doc_type' : doc_type,
            'file' : Binary(bytes_file)
            }
        db.documents.remove({'$and' : [{'user_id' : ObjectId(user_id)},{'doc_type' : doc_type}]})
        db.documents.insert_one(new_doc_for_mongo)
        form.file.data = ''
        return redirect(url_for('documents'))
    documents = list(db.documents.find({'user_id' : ObjectId(user_id)}))

    return render_template('documents.html', form=form, documents=documents)

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



    
if __name__ == '__main__':
 app.run(debug=True, port=5000)
