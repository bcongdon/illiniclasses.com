from flask import Flask, render_template, request, url_for, redirect
from data import SearchBar, CourseData
from flask.ext.pymongo import PyMongo
from db_credential import db_name, db_uri
import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps

app = Flask(__name__)


# app.config['MONGOALCHEMY_DATABASE'] = db_name
# app.config['MONGOALCHEMY_CONNECTION_STRING'] = db_uri


app.config['MONGO_DBNAME'] = db_name
app.config['MONGO_URI'] = db_uri

# db = MongoAlchemy(app)
mongo = PyMongo(app)

app.secret_key = 'development-key'

#DATA = mongo.db

# TODO
# Call API to get all courses
# and create corresponding collectinos
# and create an array that contains course names
# because we need to use this array to validate 
# user input when they search for courses

@app.route('/', methods=['GET', 'POST'])
def index():
	form = SearchBar()
	if request.method == 'POST':
		
		# Input from search bar
		user_input = form.course_name.data

		#course_collection = mongo.db.user_input
		data = mongo.db.data 
		result = data.find({'input' : user_input})
		if result.count() > 0:
			return redirect(url_for('review_page', course=user_input))
			# 
		else:
			return render_template('index.html', form=form)
	elif request.method == 'GET':
		api = requests.get('http://courses.illinois.edu/cisapp/explorer/catalog.xml')

		api_json = dumps(bf.data(fromstring(api.text)))
		print api_json
		print api.text
		return render_template('index.html', form=form)
		"""
		TODO:
		1. Check to see if course exists
		2. If yes, render_template to that route using a GET request
		3. If not, reload the page, pop-up an error message
		"""
@app.route('/foo')
def foo():
	return render_template('review.html')

@app.route('/<course>', methods=['GET', 'POST'])
def review_page(course):
		# Check to see if course is in the database
		# If yes, return the page
		# If not, return a 404
		form = CourseData()
		if request.method == 'POST':

			
			return 'test'
		elif request.method == 'GET':
			
			return render_template('review.html', foo=course, form=form)


if __name__ == '__main__':
  app.run(debug=True)



