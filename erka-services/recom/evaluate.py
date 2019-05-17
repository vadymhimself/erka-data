def retrain():
	import marshal
	from train_recomendations import train
	from create_user_data import create_db
	
	# importing data
	file = open('data/marshal_basket.dat', 'rb')
	data = marshal.load(file)
	file.close()
	print('Data has been loaded.')

	train(data[1000:], 'eval_recom_model')

	create_db(data[1000:], 'data/eval_users_data.csv')

def prepare_data():
	import marshal

	# importing data
	file = open('data/marshal_basket.dat', 'rb')
	data = marshal.load(file)[:100]
	file.close()
	print('Data has been loaded.')

	x, y = [], []
	for pur in data:
		basket = []
		if len(pur['basket']) < 2:
			continue

		for item in pur['basket']:
			basket.append(item['goodsId'])
		x.append(basket[:-1])
		y.append(basket[-1])

	return x, y

def test():
	from recom_interface import recommend

	data, target = prepare_data()
	y, n = 0, 0
	for i in range(len(data)):
		recom = recommend(data[i])
		if target[i] in [r['productId'] for r in recom]:
			y += 1
			print('right')
		else:
			n += 1
			print('wrong')
		print('{} out of {}'.format(i, len(data)))
	return y/(y + n)

def prepare_data_whole_metric():
	import marshal

	# importing data
	file = open('recom/data/marshal_basket.dat', 'rb')
	data = marshal.load(file)[:200]
	file.close()
	print('Data has been loaded.')

	x, y = [], []
	for pur in data:
		basket = []
		if len(pur['basket']) < 2:
			continue

		for item in pur['basket']:
			basket.append(item['goodsId'])
		x.append(basket[0])
		y.append(basket[1:])

	return x, y

def test_whole_metric():
	from recom_interface import recommend

	data, target = prepare_data_whole_metric()
	result = []
	for i in range(len(data)):
		recom = recommend([data[i]], num_rec=100000)
		rec_goods = [r['productId'] for r in recom]
		result.append([rec_goods.index(good) for good in target[i] if good in rec_goods])
		print('{} out of {}'.format(i, len(data)))
	return result

def prep_assoc_data():
	import pandas as pd

	df = pd.read_csv('/home/daniil/Desktop/my_files/Projects/e-com/erka-services/recom/top_orders.csv')
	receipts = list(set(df['receipt number']))[:200]
	x, y = [], []
	for receipt in receipts:
		a = df.loc[df['receipt number'] == receipt]['goodsId'].tolist()
		x.append(a[0])
		y.append(a[1:])

	return x, y


def test_whole_metric_assoc():
	import pandas as pd

	data, target = prep_assoc_data()
	associated_rules = pd.read_csv('/home/daniil/Desktop/my_files/Projects/e-com/erka-services/data/rules1.csv')
	
	def rec(index):
		def get_recommends(index):
			rules = associated_rules[associated_rules.antecedents.apply(lambda x: index in x)]
			rules = [item[0] for item in list(sorted(rules.loc[:, ['consequents', 'confidence']].values.tolist(), key=lambda x: x[1], reverse=True))]

			return rules

		rules = get_recommends(str(index))
	    
		return list(set([int(item) for s in rules for item in s[s.find("{")+1:s.find("}")].split(',')]))

	result = []
	for i in range(len(data)):
		re_goods = rec(data[i])

		if len(set(target[i]).intersection(set(re_goods))) > 0:
			result.append(1)
		else:
			result.append(0)
		print('{} out of {}'.format(i, len(data)))

	return result

if __name__ == '__main__':
	acc = test_whole_metric_assoc()
	print(acc)