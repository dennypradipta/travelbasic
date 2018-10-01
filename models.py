import datetime 
from mongoengine import *

connect('travelbasic')

class Passports(Document):
	passport_num = StringField(required=True)
	name = StringField(required=True)
	issue = StringField(required=True)
	issue_n = StringField(required=True)
	nation = StringField(required=True)
	nation_n = StringField(required=True)
	birthdate = DateTimeField(required=True)
	sex = StringField(required=True)
	expirydate = DateTimeField(required=True)
	image = StringField(required=True)
	image_path = StringField(required=True)
	created_at = DateTimeField(required=True, default=datetime.datetime.now())
	modified_at = DateTimeField(required=True, default=datetime.datetime.now())

class Users(Document):
	username = StringField(required=True)
	password = StringField(required=True)
	role = StringField(required=True)
