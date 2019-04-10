import pandas as pd
import numpy as np
import turicreate as tc

def train(data, save_path):
	arr = []
	for customer_id, basket in enumerate(data):
		interval_check = []
		for product in basket['basket']:
			check_duplicate = list(map(lambda x: x[1] == product['goodsId'], interval_check))
			if True not in check_duplicate:
				interval_check.append([int(customer_id), int(product['goodsId']), int(product['quantity'])])
			else:
				interval_check[check_duplicate.index(True)][2] += product['quantity'] 
		arr += interval_check

	data = pd.DataFrame(np.array(arr), columns=['customerId', 'productId', 'purchase_count'])

	def create_data_dummy(data):
		data_dummy = data.copy()
		data_dummy['purchase_dummy'] = 1
		return data_dummy

	data_dummy = create_data_dummy(data)

	def model(data):
		model = tc.item_similarity_recommender.create(tc.SFrame(data), user_id='customerId', item_id='productId', target='purchase_dummy', similarity_type='cosine')
		return model

	recom_model = model(data_dummy)
	recom_model.save(save_path)