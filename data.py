from flask_wtf import Form 
from wtforms import StringField, SubmitField


class SearchBar(Form):
	course_name = StringField('Enter a course...')
	submit = SubmitField('Search')

class CourseData(Form):
	review = StringField('Write a review...')
	tip = StringField('Write a tip...')
	submit = SubmitField('Submit')
