import json
from sklearn.model_selection import train_test_split
import numpy as np

data_path = './sepsis_tune_id.json'

train = dict()
val = dict()
test = dict()

# read from json
with open(data_path) as f:
    d = json.load(f)

    # print stats
    for key in d.keys():
        data = d[key]
        train_val_ids, test_ids = train_test_split(data, test_size=0.2)
        train_ids, val_ids = train_test_split(train_val_ids, test_size=0.2)

        print('---')
        print(len(data))
        print(len(train_ids))
        print(len(val_ids))
        print(len(test_ids))

        train[key] = train_ids
        val[key] = val_ids
        test[key] = test_ids

with open('train.json', 'w') as f:
    json.dump(train, f)

with open('val.json', 'w') as f:
    json.dump(val, f)

with open('test.json', 'w') as f:
    json.dump(test, f)