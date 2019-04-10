import json
import marshal

PATH = "/Users/andreybezumennui/Downloads/erka-services/basket_orders.json"
MARSHAL_PATH = "/Users/andreybezumennui/Downloads/erka-services/marshal_basket.dat"


def change_orders():
    with open(PATH, 'r') as jfr:
        orders = json.load(jfr)
    new_orders = []
    for order in orders:
        if type(order) != int:
            new_orders.append({'basket':order['basket']})

    # with open('basket_orders.json', 'w') as outfile:
    #     json.dump(new_orders, outfile)

    ouf = open('marshal_basket.dat', 'wb')
    marshal.dump(new_orders, ouf)
    ouf.close()


def load_marshal():
    inf = open(MARSHAL_PATH, 'rb')
    a = marshal.load(inf)
    inf.close()
    return a


if __name__ == '__main__':
    change_orders()