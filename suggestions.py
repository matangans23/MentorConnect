from pymongo import MongoClient
import json
import urllib
from datetime import date
import urllib.request
from bson.json_util import dumps


client = MongoClient('localhost', port=27017)

db = client["mentor_connect"]

collMentors = db["mentors"]

collMentees = db["mentees"]

def suggest(name):
	mentee = collMentees.find({"name": name})
	return mentee

	