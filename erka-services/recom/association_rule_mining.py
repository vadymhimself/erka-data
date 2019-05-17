import numpy as np  
import pandas as pd  
from apyori import apriori 

def train(data, save_path):
	def create_data(data):
		records = []  
		[records.append(list(set([prod['goodsId'] for prod in basket['basket']]))) for basket in data]
		return records

	records = create_data(data)
	print(records)

	def model(data):
		association_rules = list(apriori(records, min_support=0.1, min_confidence=0.2, min_lift=3, min_length=2)) # 1/335900
		return association_rules

	print(model(records))

if __name__ == '__main__':
	import marshal

	with open('data/marshal_basket.dat', 'rb') as file:
		data = marshal.load(file)[:10]
	print('Data has been loaded.')
	
	train(data, 'association_rule_model/assoc_recom_model')