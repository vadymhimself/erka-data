import pandas as pd
import turicreate as tc
import pickle

PATH_RECOM_MODEL = 'recom/recom_model'
recom_model = tc.load_model(PATH_RECOM_MODEL)
print('Model has been loaded.')

data = pd.read_csv('recom/data/users_data.csv')
max_order = len(data.columns) - 2

with open("recom/data/most_popular.txt", "rb") as fp:
    most_popular = pickle.load(fp)
print('Data has been loaded.')


def most_similar_id(values):
    index = 0
    max_val = values[0]
    for i, value in enumerate(values):
        if value[0] > max_val[0]:
            max_val = value
            index = i
        elif value[0] == max_val[0]:
            if value[1] < max_val[1]:
                max_val = value
                index = i

    if max_val[0] == 0:
        # no sutable id was found
        return -1
    return index


def recommend(list_of_goods, num_rec=10, last_trial=False):
    list_of_goods = set(int(good_id) for good_id in list_of_goods)
    if len(list_of_goods) == 0:
        return [{'productId': item, 'score': '0'} for item in most_popular]

    values = list(map(lambda x: [len(set(x).intersection(list_of_goods)), len([i for i in x if i != -1])],
                      data.loc[:, 'prod0':'prod{}'.format(max_order - 1)].values.tolist()))
    user = most_similar_id(values)
    if user == -1:
        if last_trial:
            return [{'productId': item, 'score': '0'} for item in most_popular]
        return []
    return list(recom_model.recommend(users=[user], k=num_rec))