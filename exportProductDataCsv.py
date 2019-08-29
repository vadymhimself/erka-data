# exports product data from mongodb in csv for google analytics
# csv format: id, name, manufacturer, category
# params: mongodb ip address(1), mongodb port(2)

from pymongo import MongoClient
import csv
import sys

ip = sys.argv[1] or '127.0.0.1'
port = sys.argv[2] or '27017'
client = MongoClient('mongodb://{}:{}'.format(ip))
db = client['xcom-prod']
goods = db.goods.find({})
data = [['ga:productSku', 'ga:productName',
         'ga:productBrand', 'ga:productCategoryHierarchy']]

for i, item in enumerate(goods):
    print('{}/{}'.format(i, goods.count()), end='\r')

    if not item.get('siteCatId', None):
        continue
    cat_strings = []
    cat_3 = db.categories.find_one({'id': item['siteCatId']})
    cat_strings.append(cat_3['name'])
    cat_2 = db.categories.find_one({'id': cat_3['parentId']})
    if cat_2:
        cat_strings.append(cat_2['name'])
        cat_1 = db.categories.find_one({'id': cat_2['parentId']})
        if cat_1:
            cat_strings.append(cat_1['name'])
    data.append([item['id'], item['name'], item.get('manufacturer', '-'),
                 '/'.join(cat_strings)])

with open('export.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(data)

csv_file.close()
print('done')
