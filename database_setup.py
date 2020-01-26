from pymongo import MongoClient
import json
import urllib
from datetime import date
import urllib.request

client = MongoClient('localhost', port=27017)

db = client["mentor_connect"]
collMentors = db["mentors"]
collMentors.drop()
collMentees = db["mentees"]
collMentees.drop()

def addMentee(email, brown_id, name, year, concentration, courses_taken, planned_courses, areas_of_help):
    to_load = {
        "email" : email,
        "brown_id": brown_id,
        "name" : name,
        "year" : year,
        "concentration" : concentration,
        "courses_taken" : courses_taken,
        "planned_courses" : planned_courses,
        "areas_of_help" : areas_of_help,
        "matched" : []
    }
    print(to_load)
    collMentees.insert_one(to_load)

def addMentor(email, brown_id, name, year, concentration, courses_taken, areas_of_help):
    to_load = {
        "email" : email,
        "brown_id" : brown_id,
        "name" : name,
        "year" : year,
        "concentration" : concentration,
        "courses_taken" : courses_taken,
        "areas_of_help" : areas_of_help,
        "matched" : []
    }
    collMentors.insert_one(to_load)

addMentee("hosasdf@gmail.com" , "hzaki1", "Hossam", "2022", "Computational Biology", ["CSCI 0150", "CSCI 0160", "CSCI1810" ], ["CSCI 1320", "CSCI 1430", "CSCI 1950Y"] , ["Y", "Y", "N", "N", "Y"])

addMentor("nash@gmail.com" ,"nahmed1", "Nasheath", "2019", "Computational Biology", ["CSCI 0150", "CSCI 0160", "CSCI1810", "CSCI 1320", "CSCI 1430", "CSCI 1950Y" ], ["Y", "Y", "N", "N", "Y"])

addMentor("mat@gmail.com" ,"mgans23", "Matan", "2020", "Computer Science", ["CSCI 0150", "CSCI 0160", "CSCI 0060", "CSCI 1951A", "CSCI 1950Y" ], ["Y", "N", "Y", "N", "N"])

addMentor("george@gmail.com" ,"grusu", "george", "2020", "Computational Biology", ["CSCI 0150", "CSCI 0160", "CSCI 0060", "CSCI 1951A", "CSCI 1950Y" ], ["Y", "Y", "N", "N", "Y"])

addMentor("tingy@gmail.com" ,"iting", "ting", "2022", "Computational Biology", ["CSCI 0150", "CSCI 0160", "CSCI 0060", "CSCI 1951A", "CSCI 1410", "CSCI 2020", "CSCI 1310"], ["Y", "Y", "N", "N", "Y"])