import json
import requests
import pandas as pd
import random

df = pd.read_csv('data/meds.csv')

def find_name(id):
	return df.loc[df['id'] == id].iloc[0]['name']

ids = [random.choice(df['id'].values) for i in range(200)]
d = {}
for id in ids:
	print(id)
	resp = requests.post('http://127.0.0.1:5000/get_similar_products', data=json.dumps({"id": str(id), 'length_restriction': 10}), headers={'Content-Type': 'application/json'}, auth=('erka-services', 'erka-products'))
	if resp.status_code == 200:
		data = resp.json()['similar']
		print(data)
		d[find_name(id)] = [item['name'] for item in data]

with open("similar_products_comp.json", "w") as write_file:
	json.dump(d, write_file)