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

if __name__ == '__main__':
	acc = test()
	print(acc)