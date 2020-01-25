from pymongo import MongoClient
import json
import urllib
from datetime import date
import urllib.request

client = MongoClient('localhost', port=27017)

db = client["mentor_connect"]

collMentors = db["mentors"]

collMentees = db["mentees"]

def addMentee(name, year, concentration, courses_taken, planned_courses, areas_of_help):
    to_load = {
        "name" : name,
        "year" : year,
        "concentration" : concentration,
        "courses_taken" : courses_taken,
        "planned_courses" : planned_courses,
        "areas_of_help" : areas_of_help
    }
    collMentees.insert_one(to_load)

def addMentor(name, year, concentration, courses, areas_of_help):
    to_load = {
        "name" : name,
        "year" : year,
        "concentration" : concentration,
        "courses" : courses,
        "areas_of_help" : areas_of_help
    }
    collMentors.insert_one(to_load)

addMentee("Hossam", "2022", "computational Biology", "CSCI 0150", "CSCI 0160", "[YNYNY]")