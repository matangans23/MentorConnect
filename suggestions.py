from pymongo import MongoClient
import json
import urllib
from datetime import date
import urllib.request
from bson.json_util import dumps
from queue import PriorityQueue



client = MongoClient('localhost', port=27017)

db = client["mentor_connect"]

collMentors = db["mentors"]

collMentees = db["mentees"]

def suggest(brown_id):
	mentee = collMentees.find({"brown_id": brown_id})[0]
	score_dict = {}
	for mentor in collMentors.find():
		score_dict[mentor["brown_id"]] = 0
		if int(mentor["year"]) >= int(mentee["year"]):
			continue
		if mentor["concentration"] == mentee["concentration"]:
			score_dict[mentor["brown_id"]] += 20
		mentor_course_set = set()
		for course in mentor["courses"]:
			mentor_course_set.add(course)
		for planned_course in mentee["planned_courses"]:
			if planned_course in mentor_course_set:
				score_dict[mentor["brown_id"]] += 3
		for taken_course in mentee["planned_courses"]:
			if taken_course in mentor_course_set:
				score_dict[mentor["brown_id"]] += 1
		for i in range(0, len(mentor["areas_of_help"])):
			if mentor["areas_of_help"][i] == mentee["areas_of_help"][i]:
				score_dict[mentor["brown_id"]] += 4
	q = PriorityQueue()
	for person in score_dict:
		q.put((-score_dict[person], person))
	topFivePeople = []
	print(q)
	while not q.empty():
		print(q.get())
	print(score_dict)
	return topFivePeople

print(suggest("hzaki1"))
