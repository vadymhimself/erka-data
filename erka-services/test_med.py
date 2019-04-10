import json
from main import app

app.testing = True
client = app.test_client()

class TestAnalytics:
    def __init__(self, host, client):
        self.url_similar_products = host + 'get_similar_products' if host[-1] == '/' else host + '/get_similar_products'
        self.url_att_products = host + 'get_att_products' if host[-1] == '/' else host + '/get_att_products'
        self.client = client

        with open('data/test_data.json', 'r') as data:
            test_data = json.load(data)
        self.test_similar_data = test_data['similar_products']
        self.test_att_data = test_data['att_products']

    def test_similar_products(self):
        for test in self.test_similar_data:
            resp = self.client.post(self.url_similar_products, data=json.dumps({"id": test['req']}), headers={'Content-Type': 'application/json'})

            assert resp.content_type == 'application/json'
            assert resp.status_code == 200
            assert set(map(lambda x: x['id'], json.loads(resp.data)['similar'])) == set(map(lambda x: x['id'], test['res']['similar']))

    def test_att_products(self):
        for test in self.test_att_data:
            resp = self.client.post(self.url_att_products, data=json.dumps({"id": test['req']}), headers={'Content-Type': 'application/json'})

            assert resp.content_type == 'application/json'
            assert resp.status_code == 200
            assert json.loads(resp.data) == test['res']

    def run_tests(self):
        self.test_similar_products()
        self.test_att_products()

def creating_tests(test_ids=[37392, 96677, -2]):
    try:
        os.remove('data/test_data.json')
    except OSError:
        pass

    with open('data/test_data.json', 'w') as f:
        json.dump(
            {'similar_products':
                [{'req': id, 'res': json.loads(client.post('http://127.0.0.1:5000/get_similar_products', data=json.dumps({"id": id}), headers={'Content-Type': 'application/json'}).data)} for id in test_ids],
            'att_products':
                [{'req': id, 'res': {"attendants": [{"name": "name1", "id": "id1", "score": 1.0}, {"name": "name2", "id": "id2", "score": 1.0}]}} for id in test_ids]}, 
        f)

if __name__ == '__main__':
    test = TestAnalytics('http://127.0.0.1:5000/', client=client)
    test.run_tests()