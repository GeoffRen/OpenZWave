import time
from pandas import read_csv
from shower_analysis.supervised_analysis import neural_network
from influxdb import InfluxDBClient


DATABASE = 'example'
TEST_DATA = 'geoff_water_test.csv'
TIME_INTERVAL = 1


def to_influx(humidity, prediction, actual):
    return [{
        "measurement": "example",
        "time": time.asctime(time.localtime()),
        "fields": {
            'humidity': humidity,
            'prediction': prediction,
            'actual': actual
        }
    }]


# Read in data
test_data = read_csv(TEST_DATA)
test_X = test_data.loc[:, ['data', 'prev_type_val', 'humidity_change_1']].astype('int').as_matrix()
test_y = test_data.loc[:, 'type_val'].astype('int').as_matrix()

client = InfluxDBClient(database=DATABASE)
nn = neural_network()
predictions = nn[0].predict(nn[1].transform(test_X))

print(type(test_X), type(test_y), type(predictions))
print(test_X.shape, test_y.shape, predictions.shape)

cur = 1
total_len = len(predictions)
for humidity, prediction, actual in zip(test_X[:, 0], test_y, predictions):
    client.write_points(to_influx(humidity, prediction, actual))
    print("{}/{} Wrote {}, {}, {} to {}".format(cur, total_len, humidity, prediction, actual, DATABASE))
    cur += 1
    time.sleep(1)
