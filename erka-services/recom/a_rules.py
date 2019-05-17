import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import time
import datetime
NUM = 350000
# MIN_SUPPORT = 0.00015625
MIN_SUPPORT = 7.8125e-05


df = pd.read_csv("/Users/skondrat/repo/deepml/erka-services/data/orders_unzipped_big_350k.csv")
# df = df.sample(NUM)
# df.to_csv("/Users/skondrat/repo/deepml/erka-services/data/orders_unzipped_big_350k.csv", index=False)
# df = df[NUM*3:NUM*4]
print(df.shape)

print("BUILDING BASKET")
#one hot encoding
start = time.time()
basket = df.groupby(["id", "item"])["quantity"].sum().unstack().reset_index().fillna(0).set_index("id")
end = time.time()
print(end - start)

# print("CONCATING BASKET")
# start = time.time()
# basket = pd.concat(baskets).fillna(0)
# end = time.time()
# print(end - start)
# sdf = basket.to_sparse()
# print("SAVING BASKET")
#
# start = time.time()
# sdf.to_csv("/Users/skondrat/repo/deepml/erka-services/data/basket_sparse.csv")
#
# end = time.time()
# print(end - start)
# print("SAVING BASKET")
# start = time.time()

# basket.to_csv("/Users/skondrat/repo/deepml/erka-services/data/basket.csv")

# end = time.time()
# print(end - start)

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1


print("FINDING BASKET SUPPORT")
print(MIN_SUPPORT)
start = time.time()
basket_sets = basket.applymap(encode_units)
frequent_itemsets = apriori(basket_sets, min_support=MIN_SUPPORT, use_colnames=True)
frequent_itemsets.to_csv("/Users/skondrat/repo/deepml/erka-services/data/frequent_itemsets1.csv")
end = time.time()
print(frequent_itemsets.shape)
print(end - start)



print("BUILDING ASSOCIATION RULES")
start = time.time()
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)
rules.to_csv("/Users/skondrat/repo/deepml/erka-services/data/rules1.csv")
print(rules.shape)
end = time.time()
print(end - start)


#TODO sort by some metric value (like confidence)
def get_recommends(index):
    return rules[rules.antecedents.apply(lambda x: index in x)]["consequents"].tolist()

print("GETTING A LIST OF RECOMMENDATIONS")
start = time.time()
get_recommends(114892)
end = time.time()
print(end - start)


