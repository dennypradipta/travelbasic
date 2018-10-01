import json, datetime
from bson import ObjectId
from flask import make_response

def json_response(obj, cls=None):
	response = make_response(json.dumps(obj, cls=cls))
	response.content_type = 'application/json'

	return response

class JSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		if type(o) is datetime.date or type(o) is datetime.datetime:
			return o.isoformat()
		return json.JSONEncoder.default(self, o)