from flask import Flask, render_template, request, url_for, redirect
from data import SearchBar, CourseData
from flask.ext.pymongo import PyMongo
from db_credential import db_name, db_uri
import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps
from setup import update


app = Flask(__name__)

app.config['MONGO_DBNAME'] = db_name
app.config['MONGO_URI'] = db_uri

mongo = PyMongo(app)

app.secret_key = 'development-key'

@app.route('/', methods=['GET', 'POST'])
def index():
	search_form = SearchBar()
	if request.method == 'GET':
		return render_template('index.html', form=search_form)

	elif request.method == 'POST':
		
		# Input from search bar
		user_input = search_form.course_name.data
		# Convert to uppercase and remove white spaces
		user_input = user_input.upper().replace(" ", "")
		# Get department id (e.g. CS) and course number in form of strings
		department_id = ''.join([char for char in user_input if char.isdigit() != True])
		course_number = ''.join([char for char in user_input if char.isdigit() == True])

		if is_input_valid(department_id, course_number) == True:
			return redirect(url_for('review_page', course=department_id+course_number))
		else:
			#return render_template('index.html', form=search_form)
			return redirect(url_for('index'))

@app.route('/<course>', methods=['GET', 'POST'])
def review_page(course):
		# Check to see if course is in the database
		# If yes, return the page
		# If not, return a 404
		review_form = CourseData()
		search_form = SearchBar()

		if request.method == 'POST':
			return 'test'
		elif request.method == 'GET':
			# Convert to uppercase and remove white spaces
			course = course.upper().replace(" ", "")
			# Get department id (e.g. CS) and course number in form of strings
			department_id = ''.join([char for char in course if char.isdigit() != True])
			course_number = ''.join([char for char in course if char.isdigit() == True])

			if is_input_valid(department_id, course_number):
				# Get description from database
				course = department_id + ' ' + course_number
				get_course = mongo.db[str(department_id)].find_one({'course_id': course})
				description = get_course['course_description']
				#description = get_course['course_description']
				return render_template('review.html', foo=course, des=description, form=review_form)
			else:
				return redirect(url_for('index'))

# Check to see if a course input is valid
def is_input_valid(department_id, course_number):
	course = department_id + ' ' + course_number

	# Get a list of departments (collections) from database
	all_departments = mongo.db.collection_names()

	# Check if input is valid
	if department_id not in all_departments:
		return False
	else:
		result = mongo.db[str(department_id)].find_one({'course_id': course})
		print result
		if result == None:
			return False 
		return True

if __name__ == '__main__':
  app.run(debug=True)



