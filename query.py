#!/usr/bin/python3

from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
import re
from pymongo import MongoClient
import json
import urllib
from datetime import date
import urllib.request
from bson.json_util import dumps
from queue import PriorityQueue



client = MongoClient('localhost', port=27017)
global list_of_docs
list_of_docs = []
db = client["mentor_connect"]

collMentors = db["mentors"]

collMentees = db["mentees"]

app = Flask(__name__)
Bootstrap(app)

# This is for the form submission, don't worry about it being secure.
app.config['SECRET_KEY'] = 'penguinsrulelots'

names = set()
concentrations = set()
courses = set()
helped = set()

for docs in collMentors.find():
    names.add(docs['name'])
    concentrations.add(docs['concentration'])
    for course in docs['courses']:
        courses.add(course)
    for help in docs['areas_of_help']:
        helped.add(help)

@app.route('/search', methods=['POST', 'GET']) #TODO
def main_page():
    print(list_of_docs)
    return render_template('filter_page.html', names=names, concentrations=concentrations, courses = courses, helped = helped, list_of_docs = list_of_docs)
    # TODO: Handle serving the main page and AddForm submission here.

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


app.run(debug=True)