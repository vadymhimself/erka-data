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

if __name__ == '__main__':
    import pickle

    with open("data/most_popular.txt", "wb") as fp:
        pickle.dump(get_popular(), fp)