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
from setup_helper import get_latest_classes

app = Flask(__name__)


app.config['MONGO_DBNAME'] = db_name
app.config['MONGO_URI'] = db_uri

mongo = PyMongo(app)

api_classes = get_latest_classes("CS")

for ui_class in api_classes:
	# if ui_class['@id'] == 225:
	# if ui_class['@id'] == 125:
	if ui_class['@id'] == 374:
		api_response = requests.get(ui_class['@href'])
		api_json = bf.data((fromstring(api_response.text)))
		# print dumps(api_json)

		couse_page = api_json['{http://rest.cis.illinois.edu}course']
		label = couse_page['label']['$']
		description = couse_page['description']['$']

		print "Label: " + label + "\nDescription: " + description



# ---------------- Example Collection ------------------------------
# Collection : 225
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
# 	"review" : "Like other people have said, there is no magic. 
#				It will be challenging sometimes, but you will learn a lot. 
#				Heres some tips: Learning in C++ syntax would be great. 
#				Start your MPs early. Other than that, enjoy the class."
# 	"teacher_review" : ("Cinda Heeren","4.4")
# 	"hours" : "2.7"
# }
# ------------------------------------------------------------------