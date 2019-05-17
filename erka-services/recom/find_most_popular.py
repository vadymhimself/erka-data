def get_popular(quant=5):
    import marshal

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
    most_popular = [item[0] for item in most_popular]

    return most_popular

def diff_prod():
    import marshal

    # importing data
    file = open('data/marshal_basket.dat', 'rb')
    data = marshal.load(file)
    file.close()
    print('Data has been loaded.')

    products = set()
    for pur in data:
        for item in pur['basket']:
            products.add(item['goodsId'])

    return len(products)

def dist_dataset():
    import pandas as pd
    import marshal

    colnames = ['Date', 'receipt number', 'warehouse number', 'quantity', 'goodsId', 'sum']
    df = pd.read_csv('/home/daniil/Desktop/my_files/Projects/e-com/Выгрузка/Sales.csv', '\t', names=colnames, header=None)

    file = open('data/marshal_basket.dat', 'rb')
    data = marshal.load(file)
    file.close()

    products = set()
    for pur in data:
        for item in pur['basket']:
            products.add(item['goodsId'])
    products |= set(df['goodsId'])

    product_data = {prod: 0 for prod in list(products)}
    for j, prod in enumerate(list(products)):
        for index, order in df.loc[df['goodsId'] == prod].iterrows():
            product_data[prod] += int(order['quantity'])
        print('{} out of {}'.format(j, len(list(products))))

    for j, pur in enumerate(data):
        for item in pur['basket']:
            product_data[item['goodsId']] += int(item['quantity'])
        print('{} out of {} orders'.format(j, len(data)))

    import json
    with open('pop_items.json', 'w') as outfile:
        json.dump(product_data, outfile)

def create_dataset():
    import json

    with open('pop_items.json', 'r') as json_file:  
        data = json.load(json_file)

    most_pop = [int(x[0]) for x in list(sorted(list(data.items()), key=lambda x: x[1], reverse=True))[:500]]

    import pandas as pd

    colnames = ['Date', 'receipt number', 'warehouse number', 'quantity', 'goodsId', 'sum']
    df = pd.read_csv('/home/daniil/Desktop/my_files/Projects/e-com/Выгрузка/Sales.csv', '\t', names=colnames, header=None)

    pop_df = df.loc[df['receipt number'].isin(list(set(df.loc[df['goodsId'].isin(most_pop)]['receipt number'])))]
    pop_df = pop_df.drop(['Date', 'warehouse number', 'quantity', 'sum'], axis=1)
    
    rec_nums = list(set(pop_df['receipt number']))

    return most_pop, rec_nums, pop_df

if __name__ == '__main__':
    # import pickle

    # with open("data/most_popular.txt", "wb") as fp:
        # pickle.dump(get_popular(), fp)

    most_pop, rec_nums, pop_df = create_dataset()
    # for j, num in enumerate(rec_nums):
    #     if len(set(pop_df.loc[pop_df['receipt number'] == num]['goodsId']).intersection(most_pop)) > 1:
    #         nums.append(num)
    #     print('{} out of {}'.format(j, len(rec_nums)))

    d = {item: 0 for item in rec_nums}
    for j, pop in enumerate(most_pop):
        for item in pop_df.loc[pop_df['goodsId'] == pop]['receipt number'].iteritems():
            d[item[1]] += 1
        print('{} out of {}'.format(j, len(most_pop)))

    nums = [key for key, value in d.items() if value > 2]
    pop_df = pop_df.loc[pop_df['receipt number'].isin(nums)]
    print(len(pop_df))
    print(len(set(pop_df['receipt number'])))

    pop_df.to_csv('top1000_dataset2.csv')