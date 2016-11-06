from flask import Flask, render_template, request, url_for, redirect
from data import SearchBar, CourseData
from flask.ext.pymongo import PyMongo
from db_credential import db_name, db_uri
import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps

# get initial set of all the years
def get_latest_year():
	api_response = requests.get('http://courses.illinois.edu/cisapp/explorer/catalog.xml')
	api_json = bf.data(fromstring(api_response.text))
	current_year_url = api_json['{http://rest.cis.illinois.edu}schedule']['calendarYears']['calendarYear'][0]['@href']
	# print current_year_url
	return current_year_url

# get latest semester
def get_latest_semester(current_year_url):
	api_response = requests.get(current_year_url)
	api_json = bf.data(fromstring(api_response.text))
	semesters = api_json['{http://rest.cis.illinois.edu}calendarYear']['terms']['term']
	lastest_semester_url = semesters[-1]['@href']
	# print lastest_semester_url
	return lastest_semester_url

# get all coursess
def get_departments(semester_url):
	api_response = requests.get(semester_url)
	api_json = bf.data(fromstring(api_response.text))
	departments = api_json['{http://rest.cis.illinois.edu}term']['subjects']['subject']
	return departments

# get a single department
def get_department(department_url, course_id):
	api_response = requests.get(department_url)
	api_json = bf.data(fromstring(api_response.text))
	departments = api_json['{http://rest.cis.illinois.edu}term']['subjects']['subject']
	# placeholder Loop for departments
	for department in departments:
		if department['@id'] == course_id:
			# print department['@href']
			return department['@href']

def get_classes(class_url):
	api_response = requests.get(class_url)
	api_json = bf.data(fromstring(api_response.text))
	return api_json['{http://rest.cis.illinois.edu}subject']['courses']['course']

def get_latest_classes(department):
	api_latest_year = get_latest_year()
	api_latest_semester = get_latest_semester(api_latest_year)
	api_courses = get_department(api_latest_semester, department)
	api_classes = get_classes(api_courses)
	return api_classes