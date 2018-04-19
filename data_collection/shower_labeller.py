from sys import argv
from influxdb import InfluxDBClient
from dateutil.parser import parse


DATABASE = 'sterling_ranch'


# Insert same data except set type to be shower and type_val to be 1, which represents a shower in our case.
def result_set_to_influxdb_json(result_set):
    return [{
        "measurement": 'value_refresh',
        "tags": {
            'id_on_network': result_set['id_on_network'],
            'home_id': result_set['home_id'],
            'node_id': result_set['node_id'],
            'value_id': result_set['value_id'],
            'manufacturer_id': result_set['manufacturer_id'],
            'product_id': result_set['product_id'],
            'label': result_set['label']
        },
        "time": result_set['time'],
        "fields": {
            'data': float(result_set['data']),
            'units': result_set['units'],
            'type': 'shower',
            'type_val': 1
        }
    }]


client = InfluxDBClient(database='sterling_ranch')
q = "select * from value_refresh where time > '{}' and time  < '{}'".format(parse(argv[1]), parse(argv[2]))
res = client.query(q)
res = list(res.get_points())
for result_set in res:
    client.write_points(result_set_to_influxdb_json(result_set))
    print("Changed type to shower for time: {} label: {} data: ".format(result_set['time'], result_set['label'], result_set['data']))
print("Changed {} number of data points".format(len(res)))
