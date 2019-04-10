import pandas as pd

def create_db(data, save_path):
	max_order = len(max(data, key=lambda x: len(x['basket']))['basket'])
	def pad_list(arr):
		if len(arr) == max_order:
			return arr
		elif len(arr) < max_order:
			arr += [-1]*(max_order - len(arr))
			return arr

	data = pd.DataFrame.from_dict({customer_id: pad_list([int(product['goodsId']) for product in basket['basket']]) for customer_id, basket in enumerate(data)}, 
								   columns=['prod{}'.format(i) for i in range(max_order)], orient='index')
	data.to_csv(save_path)