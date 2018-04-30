from sys import argv
from influxdb import InfluxDBClient
from dateutil.parser import parse


# InfluxDB database name to use.
DATABASE = 'sterling_ranch'


def set_as_shower(result_set):
    """Sets result_set to a shower instance.
    :param result_set: A single unlabeled instance.
    :return: result_set as a shower instance.
    """
    result_set['fields']['type'] = 'shower'
    result_set['fields']['type_val'] = 1
    return result_set


# Query the database for all values between the two given times.
client = InfluxDBClient(database='sterling_ranch')
q = "select * from value_refresh where time > '{}' and time  < '{}'".format(parse(argv[1]), parse(argv[2]))
res = client.query(q)
res = list(res.get_points())

# Update all the queried for data points and then write them back.
# InfluxDB as of 04/27/2018 does not support update, this is how you have to update data.
for result_set in res:
    client.write_points(set_as_shower(result_set))
    print("Changed type to shower for time: {} label: {} data: "
          .format(result_set['time'], result_set['label'], result_set['data']))
print("Changed {} number of data points".format(len(res)))
