from flask_wtf import Form 
from wtforms import StringField, SubmitField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length


class SearchBar(Form):
	course_name = StringField('Enter a course...', validators=[DataRequired(), Length(min=5)])
	submit = SubmitField('Search')

class CourseData(Form):
	review = StringField(widget=TextArea(), validators=[DataRequired(), Length(min=10)])
	hours = SelectField(
        'Number of hours',
        choices=[('question', 'Did you have a life? (workload per week)'), 
        ('Below 3 hours', 'Below 3 hours'), ('3 to 6 hours', '3 to 6 hours'), ('7 to 10 hours', '7 to 10 hours'), ('11 to 14 hours', '11 to 14 hours'),
        ('15 to 18 hours', '15 to 18 hours'), ("I didn't have a life", "I didn't have a life")], validators=[DataRequired()]
    )
	submit = SubmitField('Submit')
