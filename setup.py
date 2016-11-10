from flask import Flask, render_template, request, url_for, redirect
from data import SearchBar, CourseData
from flask.ext.pymongo import PyMongo
from db_credential import db_name, db_uri
import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps
# from json import loads
# import datetime
from setup_helper import get_latest_classes, get_all_departments

# app = Flask(__name__)


# app.config['MONGO_DBNAME'] = db_name
# app.config['MONGO_URI'] = db_uri

# mongo = PyMongo(app)

# app.secret_key = 'development-key'

# class_name = "cs374"
# mongo.db[class_name].insert({})

# api_classes = get_latest_classes("CS")

def update():
	app = Flask(__name__)
	app.config['MONGO_DBNAME'] = db_name
	app.config['MONGO_URI'] = db_uri

	mongo = PyMongo(app)

	app.secret_key = 'development-key'

	departments = get_all_departments()

	for department in departments:

		department_id = department['@id']

		# print departments_id <-works

		# department_list = department
		api_response = requests.get(department['@href'])
		department_page = bf.data(fromstring(api_response.text))
		# print dumps(department_page) <-works!!

		department_courses = department_page['{http://rest.cis.illinois.edu}subject']['courses']['course']
		for ui_class in department_courses:
			class_name = str(department_id) + str(ui_class['@id'])
			

			api_response = requests.get(ui_class['@href'])
			api_json = bf.data((fromstring(api_response.text)))
			print dumps(api_json)

			couse_page = api_json['{http://rest.cis.illinois.edu}course']
			label = couse_page['label']['$']
			description = couse_page['description']['$']

			# print "Label: " + label + "\nDescription: " + description
			mongo.db[class_name].insert({	'description' : description,
											'avg_hours' : 0
										})



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
#				Heres some tips: Learning in C++ syntax would be great and 
#				start your MPs early. Other than that, enjoy the class."
# 	"teacher_review" : ("Cinda Heeren","4.4")
# 	"hours" : "2.7"
# }
# ------------------------------------------------------------------