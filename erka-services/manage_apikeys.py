import secrets
import json

def generate_key(quota):
	'''
		generate new key
	'''
	if not isinstance(quota, int):
		raise ValueError("'quota' must be int.")
	if quota < 0:
		raise ValueError("'quota' must be non negative.")

	with open('apikeys.json', 'r') as apikey:
		keys = json.load(apikey)
	
	new_key = secrets.token_urlsafe(40)
	while new_key in keys.keys():
		new_key = secrets.token_urlsafe(40)

	keys[new_key] = {'quota': quota, 'requests_done': 0}

	with open('apikeys.json', 'w') as apikey:
		json.dump(keys, apikey)

	return new_key

def update_requests(api_key, num_req=0):
	'''
		update number of requests done by api key
	'''
	if not isinstance(num_req, int):
		raise ValueError("'num_req' must be int.")
	if num_req < 0:
		raise ValueError("'num_req' must be non negative.")

	with open('apikeys.json', 'r') as apikey:
		keys = json.load(apikey)

	if not keys.get(api_key):
		raise ValueError("No api key was found.")

	keys[api_key]['requests_done'] = num_req

	with open('apikeys.json', 'w') as apikey:
		json.dump(keys, apikey)

def update_quota(api_key, new_quota):
	'''
		update quota by api key
	'''
	if not isinstance(new_quota, int):
		raise ValueError("'new_quota' must be int.")
	if new_quota < 0:
		raise ValueError("'new_quota' must non negative.")

	with open('apikeys.json', 'r') as apikey:
		keys = json.load(apikey)

	if not keys.get(api_key):
		raise ValueError("No api key was found.")

	keys[api_key]['quota'] = new_quota

	with open('apikeys.json', 'w') as apikey:
		json.dump(keys, apikey)

def delete_key(api_key):
	'''
		delete api key
	'''
	with open('apikeys.json', 'r') as apikey:
		keys = json.load(apikey)

	if not keys.get(api_key):
		raise ValueError("No api key was found.")

	del keys[api_key]

	with open('apikeys.json', 'w') as apikey:
		json.dump(keys, apikey)