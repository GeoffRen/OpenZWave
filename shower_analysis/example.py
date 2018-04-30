import time
from pandas import read_csv
from shower_analysis.supervised_analysis import rf
from influxdb import InfluxDBClient
import numpy as np


DATABASE = 'example'  # The InfluxDB database name to write the example data too. Allows live grafana representation.
TEST_DATA = 'geoff_water_test.csv'  # The csv to get the example data from.
TIME_INTERVAL = 1  # The time interval in seconds to write the predictions to DATABASE.


def to_influx(humidity, prediction, actual, write_time=None):
    """Formats the dummmy data.
    :param humidity: Relative humidity value.
    :param prediction: Our model's prediction of whether the instance is a shower or not.
    :param actual: Whether the instance is actually a shower or not.
    :param write_time: What the write time should be, used for updating past instances (as in optimization).
    """
    return {
        "measurement": "example",
        "time": time.asctime(time.localtime()) if write_time is None else write_time,
        "fields": {
            'humidity': humidity,
            'prediction': prediction,
            'actual': actual
        }
    }

# Read in data
test_data = read_csv(TEST_DATA)
test_X = test_data.loc[:, ['data', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
test_y = test_data.loc[:, 'type_val'].astype('int').as_matrix()

client = InfluxDBClient(database=DATABASE)  #
rf = rf()
cur = 1
total_len = len(test_data)
record = []  # Keeps track of all the data so the optimization can be used.
for humidity, point, actual in zip(test_X[:, 0], test_X, test_y):
    point = point.reshape(-1, 5)
    prediction = rf[0].predict(point)[0]
    # Optimization: set past 4 points (last minute) to a shower instance.
    if prediction == 1:
        for past_point in record[-4:]:
            client.write_points([to_influx(past_point['fields']['humidity'],
                                           np.int64(1),
                                           past_point['fields']['actual'],
                                           write_time=past_point['time'])])
    data = to_influx(humidity, prediction, actual)
    client.write_points([data])
    record.append(data)
    print("{} {}/{} Wrote {}, {}, {} to {}".format(data['time'], cur, total_len, humidity, prediction, actual, DATABASE))
    cur += 1
    time.sleep(1)