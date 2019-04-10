from IPython.display import clear_output, display
import base64
import sys
import time
import requests
import json

page_count = 9999999999999 # init with max value
# if json file is already have
with open('orders.json', 'r') as jfr:
    orders = json.load(jfr)
params = {'page': orders[-1], 'per-page':100}
# if not
# params = {'page': 0, 'per-page':100}
# orders = []


def download_all_orders():
    global page_count, orders
    auth_token = 'U2l0ZU96OkFWNzREOA=='
    headers = {'Authorization': 'Basic {}'.format(auth_token)}
    url = 'http://ws.erkapharm.com:8990/ecom/hs/orders?expand=basket'

    while params['page'] < page_count:
        started = time.time()
        res = requests.get(url, params=params, headers=headers).json()
        orders += res['orders']
        page_count = res['pageCount']
        params['page'] = params['page'] + 1
        clear_output(wait=True)
        progress = params['page'] * 1. / res['pageCount'] * 100
        ellapsed_seconds = time.time() - started
        left_seconds = ellapsed_seconds * (page_count - params['page'])
        status = 'progress: {:.2f}% Remaining: {} minutes Pages: {}'.format(progress, int(left_seconds / 60),
                                                                            params['page'])
        with open('orders.json', 'w') as outfile:
            json.dump(orders + [params['page']], outfile)

        print(status)
        f = open('status.txt', 'w')
        f.write(status)

    return orders


orders = download_all_orders()


with open('orders_complete.json', 'w') as outfile:
    json.dump(orders, outfile)