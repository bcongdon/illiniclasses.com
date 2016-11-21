from flask import Flask, render_template, request, url_for, redirect
from data import SearchBar, CourseData
from flask_pymongo import PyMongo
from db_credential import db_name, db_uri
import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps
# from json import loads
# import datetime
from database_setup_helper import get_all_departments, get_all_courses, get_a_course

def update():
	app = Flask(__name__)
	app.config['MONGO_DBNAME'] = db_name
	app.config['MONGO_URI'] = db_uri

	mongo = PyMongo(app)

	app.secret_key = 'development-key'

	all_departments_arr = get_all_departments()

	# Return a list of all collections (departments in mlab)
	all_collections = mongo.db.collection_names()

	# Populate each department as a collection 
	# in MongoDB
	for each_department in all_departments_arr:
		department_id = each_department['@id']			# e.g. CS
		
		# Create a new collection for each department if
		# it's not already there
		if department_id in all_collections:
			continue
		mongo.db[str(department_id)].insert({})			

		# Departments with little information will be passed
		if (department_id == 'BIOL' or department_id == 'ENT' 
			or department_id == 'PBIO' or department_id == 'WGGP'):
			continue

		# Populate each course as an object for 
		# each department in MongoDB
		department_url = each_department['@href']
		all_courses_arr = get_all_courses(department_url)

		for each_course in all_courses_arr:	
			course_url = each_course['@href']			# Get course API URL
			course = get_a_course(course_url)			# Get a course in JSON format

			course_id = course['@id']
			course_name = course['label']['$']
			if 'description' not in course:
				continue
			course_description = course['description']['$']
			mongo.db[str(department_id)].insert({'course_id': course_id, 
				'course_name': course_name, 'course_description': course_description})
			
	

# ---------------- Example Collection ------------------------------
# Collection Name : CS225
#  
# First element:
# {
# 	"description" : "blah blah data structures blah blah implentations blah blah"
# 	"avg_hours" : 4.2
# 	"proffessors" : [("Ganna Yershova", 4.2), ("Cinda Heeren", 4.5)]
# 						^ 			 	 ^
# 					   Name 		  avg_score
# }
# 
# Reviews:
# {
# 	"user" : "pitlv2109"
# 	"score" : "4"
# 	"review" : "Like other people have said, there is no magic. 
#				It will be challenging sometimes, but you will learn a lot. 
#				Here are some tips: Learning in C++ syntax would be great and 
#				start your MPs early. Other than that, enjoy the class."
# 	"teacher_review" : ("Cinda Heeren","4.4")
# 	"hours" : "2.7"
# }
# ------------------------------------------------------------------