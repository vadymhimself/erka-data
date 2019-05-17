def get_popular(quant=5):
    import marshal
    import pandas as pd 
    # importing data
    file = open('data/marshal_basket.dat', 'rb')
    data = marshal.load(file)
    file.close()
    print('Data has been loaded.')

    products = {}
    for pur in data:
        for item in pur['basket']:
            if item['goodsId'] in products.keys():
                products[item['goodsId']] += int(item['quantity'])
            else:
                products[item['goodsId']] = int(item['quantity'])
    
    most_popular = sorted(list(products.items()), key=lambda x: x[1], reverse=True)[:quant]
    most_pop = [item[0] for item in most_popular]

    order_id = -1
    d = {'receipt number': [], 'goodsId': []}
    for j, pur in enumerate(data):
        if len(set([item['goodsId'] for item in pur['basket']]).intersection(set(most_pop))) > 2:
            for item in pur['basket']:
                d['receipt number'].append(order_id) 
                d['goodsId'].append(item['goodsId'])
            order_id -= 1
        print('{} out of {}'.format(j, len(data)))
    pop_df = pd.DataFrame.from_dict(d)
    print(len(pop_df))
    print(len(set(pop_df['receipt number'])))
    pop_df.to_csv('top1000_dataset1.csv')


if __name__ == '__main__':
    get_popular(1000)