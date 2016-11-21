from flask import Flask, flash, render_template, request, url_for, redirect
from flask_wtf import Form 
from data import SearchBar, CourseData
from flask_pymongo import PyMongo
from db_credential import db_name, db_uri
import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps
# from database_setup import update 	# use to update db
import time  


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
			return redirect(url_for('index'))

@app.route('/<course>', methods=['GET', 'POST'])
def review_page(course):
	'''
	Check to see if course is in the database
	If yes, return the page
	If not, return a 404
	'''
	review_form = CourseData()
	search_form = SearchBar()
	
	# Convert to uppercase and remove white spaces
	course = course.upper().replace(" ", "")
	# Get department id (e.g. CS) and course number in form of strings
	department_id = ''.join([char for char in course if char.isdigit() != True])
	course_number = ''.join([char for char in course if char.isdigit() == True])
	course = department_id + ' ' + course_number

	if request.method == 'POST':
		# Check if all input fields are entered correctly
		if review_form.validate_on_submit() == False:
			return redirect(url_for('review_page', course=course))
		else:
			current_time = time.localtime(time.time()) 
			current_time = str(current_time.tm_mon) + "/" + str(current_time.tm_mday) + "/" + str(current_time.tm_year)
			insert_review(department_id, course, review_form.review.data, review_form.hours.data, current_time)
			return redirect(url_for('review_page', course=course))

	elif request.method == 'GET':
		if is_input_valid(department_id, course_number):
			get_course = mongo.db[department_id].find_one({'course_id': course})
			description = get_course['course_description']
			avg_color = 'N/A'
			if 'reviews' in get_course:
				reviews_list = get_course['reviews']
				avg_color = get_workload_color(get_course['avg_hours'])
			else:
				reviews_list = {}
				get_course['avg_hours'] = 'N/A'
			
			return render_template('review.html', course=get_course, avg_hours=get_course['avg_hours'], 
				avg_color=avg_color, reviews=reviews_list, des=description, form=review_form)
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
		result = mongo.db[department_id].find_one({'course_id': course})
		if result == None:
			return False 
		return True

# Insert new reviews to the database
def insert_review(department_id, course, review, hours, current_time):
	'''
	Get the reviews from the current course, append new review to the list,
	delete the current course, and insert a new one (with the new review)
	'''
	department = mongo.db[department_id]
	current_course = department.find_one({'course_id': course})
	if 'reviews' in current_course:
		new_reviews = current_course['reviews']
	else:
		current_course['avg_hours'] = 0
		current_course['reviews'] = []
		new_reviews = []

	avg_hours = get_average_workload(hours, current_course['avg_hours'], len(current_course['reviews']))
	color = get_workload_color(get_workload(hours))
	review_dict = {'hours': hours, 'review': review, 'time': current_time, 'color': color}
	new_reviews.append(review_dict)
	review_list = {'course_id': current_course['course_id'], 'course_description': current_course['course_description'], 
	'course_name': current_course['course_name'], 'avg_hours': avg_hours, 'reviews': new_reviews}
	department.delete_one({'course_id': course})
	department.insert(review_list)

	'''
	Insert to log db to keep track of all reviews
	'''
	mongo.db['LOG'].insert({'course': course, 'review': review, 'time': current_time})

	'''
	Not working yet :( Would improve efficiency significantly 
	department.update_one({'course_id:': 'CS 225'}, {'$push': {'reviews:': review_dict}})
	'''

# Parse workload from workload selectfield
def get_workload(workload_str):
	workload_dict = {'Below 3 hours': 1.5, '3 to 6 hours': 4.5, '7 to 10 hours': 8.5, 
	'11 to 14 hours': 12.5, '15 to 18 hours': 16.5, "I didn't have a life": 22.5}
	return workload_dict[workload_str]

# Calculate average workload per week
def get_average_workload(workload_str, avg_workload, num_reviews):
	return (avg_workload + get_workload(workload_str))/(num_reviews + 1)

# Choose a color for workload based on number of hours	
def get_workload_color(workload):
	workload_dict = {1.5: 'btn btn-info', 4.5: 'btn btn-info', 8.5: 'btn btn-primary', 
	12.5: 'btn btn-warning', 16.5: 'btn btn-danger', 22.5: 'btn btn-danger'}
	return workload_dict[workload]

if __name__ == '__main__':
  app.run(debug=True)



