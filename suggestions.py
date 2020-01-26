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
		if int(mentor["year"]) >= int(mentee["year"]):
			continue
		score_dict[mentor["brown_id"]] = 0
		if mentor["concentration"] == mentee["concentration"]:
			score_dict[mentor["brown_id"]] += 20
		mentor_course_set = set()
		for course in mentor["courses_taken"]:
			mentor_course_set.add(course)
		for planned_course in mentee["planned_courses"]:
			if planned_course in mentor_course_set:
				score_dict[mentor["brown_id"]] += 3
		for taken_course in mentee["planned_courses"]:
			if taken_course in mentor_course_set:
				score_dict[mentor["brown_id"]] += 1
		for i in range(0, len(mentor["areas_of_help"])):
			if mentor["areas_of_help"][i] in mentee["areas_of_help"]:
				score_dict[mentor["brown_id"]] += 4
	print(score_dict)
	topFive = {k: v for k, v in sorted(score_dict.items(), key=lambda item: item[1], reverse=True)}
	topList = []
	counter = 0
	for i in topFive:
		topList.append(collMentors.find({"brown_id": i})[0])
		counter += 1
		if counter == 2:
			break
	return topList


