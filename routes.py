from flask import Flask, render_template, request, url_for, redirect
from data import SearchBar, CourseData
from flask_pymongo import PyMongo
# from db_credential import db_name, db_uri 	# For running locally (Heroku config vars for online)
# from database_setup import update 	# Use to update db
import time
import os 								# For Heroku config vars


app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('DB_NAME')
app.config['MONGO_URI'] = os.environ.get('DB_URI')

# For running locally
# app.config['MONGO_DBNAME'] = os.environ.get('DB_NAME', db_name)
# app.config['MONGO_URI'] = os.environ.get('DB_URI', db_uri)

mongo = PyMongo(app)

app.secret_key = 'development-key'


@app.route('/', methods=['GET', 'POST'])
def index():
	search_form = SearchBar()
	if request.method == 'GET':
		LOG = mongo.db['LOG']
		return render_template('index.html', search_bar=search_form, num_reviews=LOG.count())

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
		'''
		Search bar
		'''
		# Input from search bar
		user_input = search_form.course_name.data

		if len(user_input) > 0:
			# Convert to uppercase and remove white spaces
			user_input = user_input.upper().replace(" ", "")
			# Get department id (e.g. CS) and course number in form of strings
			department_id = ''.join([char for char in user_input if char.isdigit() != True])
			course_number = ''.join([char for char in user_input if char.isdigit() == True])

			if is_input_valid(department_id, course_number) == True:
				return redirect(url_for('review_page', course=department_id+course_number))
			else:
				return redirect(url_for('review_page', course=course))

		else:
			# Check if all submission input fields are entered correctly
			if review_form.validate_on_submit() == False:
				return redirect(url_for('review_page', course=course))
			else:

				'''
				Review submission form
				'''
				current_time = time.localtime(time.time())
				current_time = str(current_time.tm_mon) + "/" + str(current_time.tm_mday) + "/" + str(current_time.tm_year)
				insert_review(department_id, course, review_form.review.data, review_form.hours.data, current_time)
				return redirect(url_for('review_page', course=course))

	elif request.method == 'GET':
		if is_input_valid(department_id, course_number):
			print "GOT A VISIT AT " + course
			get_course = mongo.db[department_id].find_one({'course_id': course})
			description = get_course['course_description']
			avg_color = 'N/A'
			if 'reviews' in get_course:
				reviews_list = get_course['reviews']
				avg_color = get_workload_color(get_course['avg_hours'])
			else:
				reviews_list = {}
				get_course['avg_hours'] = 'N/A'

			return render_template('review.html', search_bar=search_form, course=get_course, avg_hours=get_course['avg_hours'], 
				avg_color=avg_color, reviews=reviews_list, des=description, form=review_form)
		else:
			return redirect(url_for('index'))

def is_input_valid(department_id, course_number):
	""" Check to see if a course input is valid """
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
	# print "Number of reviews", len(current_course['reviews'])

	color = get_workload_color(get_workload(hours))
	review_dict = {'hours': hours, 'review': review, 'time': current_time, 'color': color}
	new_reviews.append(review_dict)
	review_list = {'course_id': current_course['course_id'], 'course_description': current_course['course_description'], 
		'course_name': current_course['course_name'], 'avg_hours': avg_hours, 'reviews': new_reviews}

	department.remove({'course_id': course})
	department.insert(review_list)

	'''
	Insert to log db to keep track of all reviews
	'''
	mongo.db['LOG'].insert({'course': course, 'review': review, 'time': current_time})

	print "GOT A REVIEW FOR " + course

	'''
	Not working yet :( Would improve efficiency significantly 
	department.update_one({'course_id:': 'CS 225'}, {'$push': {'reviews:': review_dict}})
	'''

def get_workload(workload_str):
	""" Parse workload from workload selectfield """
	workload_dict = {'0': 0, 'Below 3 hours': 1.5, '3 to 6 hours': 4.5, '7 to 10 hours': 8.5, 
	'11 to 14 hours': 12.5, '15 to 18 hours': 16.5, "I didn't have a life": 22.5}
	return workload_dict[workload_str]


def get_average_workload(workload_str, avg_workload, num_reviews):
	""" Calculate average workload per week """
	return round((avg_workload * num_reviews + get_workload(workload_str))/(num_reviews + 1), 2)


def get_workload_color(workload):
	""" Choose a color for workload based on number of hours """
	workload_dict = {1.5: 'btn btn-info', 4.5: 'btn btn-info', 8.5: 'btn btn-primary',
		12.5: 'btn btn-warning', 16.5: 'btn btn-danger', 22.5: 'btn btn-danger'}
	if workload <= 6:
		return 'btn btn-info'
	elif workload <= 10:
		return 'btn btn-primary'
	elif workload <= 14:
		return 'btn btn-warning'
	else:
		return 'btn btn-danger'

if __name__ == '__main__':
	app.run(debug=True)
