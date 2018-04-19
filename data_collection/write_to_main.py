from influxdb import InfluxDBClient
import datetime
from dateutil.parser import parse
from threading import Timer
import requests


PERSONAL_DATABASE = 'sterling_ranch'
CENTRAL_DATABASE = 'utilities_usage'
CENTRAL_DATABASE_HOST = '18.218.111.49'
# CENTRAL_DATABASE_HOST = 'localhost'
QUERY_INTERVAL = 60  # In minutes.
GALLONS_PER_15_SECONDS = 0.425


def main():
    """Calculates the water usage from your personal influxdb and inserts it into the central database every
    QUERY_INTERVAL minutes. It will start transmitting data from the last time you inserted data into the central
    database. If you've never transmitted data before, it will start calculating and transmitting from the start of
    your database.
    """
    personal_client = InfluxDBClient(database=PERSONAL_DATABASE)
    central_client = InfluxDBClient(host=CENTRAL_DATABASE_HOST, database=CENTRAL_DATABASE)
    q = "select * from water order by desc limit 1"
    last_date_in_central_database = peek(central_client.query(q).get_points())
    if not last_date_in_central_database:  # Run from the start of your database.
        initialize_central_database(personal_client)
    else:  # Run from the last time you transmitted data.
        initialize_central_database(personal_client, last_date_in_central_database['time'])
    delay = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1) \
            - datetime.datetime.now() + datetime.timedelta(seconds=1)
    Timer(delay.total_seconds(), main).start()  # Run a second past the next hour.
    print("Running again at ", datetime.datetime.now() + delay)  # Sanity check.


# Repeatedly makes queries through personal_client and writes the data to central_client starting at from_datetime
# until it exhausts all the data. The queries are between dates of size QUERY_INTERVAL.
def initialize_central_database(personal_client, from_datetime=None):
    print("\n~~~INITIALIZING CENTRAL CLIENT FROM {}~~~\n".format(from_datetime if from_datetime else "BEGINNING"))
    q = "select * from value_refresh where label = 'Relative Humidity' limit 1"
    try:
        beginning_time = from_datetime if from_datetime else next(personal_client.query(q).get_points())['time']
    except:
        raise UserWarning("ERROR: NO VALUES IN PERSONAL DATABASE")
    beginning_time = parse(beginning_time).replace(microsecond=0, second=0, minute=0)  # So time across users is synced.
    end_time = increment(beginning_time)
    # Since thie query is guaranteed to work, data is a dict containing all the identifying information of the sensor.
    identifying_data = peek(personal_client.query(q).get_points())
    # Now, get and write water usage per QUERY_INTERVAL and identifying_data to central_client.
    while end_time < hacky_datetime_now():
        q = "select * from value_refresh where label = 'Relative Humidity' and time >= '{}' and time  < '{}'"\
            .format(beginning_time.isoformat(), end_time.isoformat())
        res = list(personal_client.query(q).get_points())
        # Since data is collected in intervals of 15 seconds, each point that has type_val = 1 represents 1
        # GALLONS_PER_15_SECONDS water used.
        water_usage = sum(data['type_val'] for data in res) * GALLONS_PER_15_SECONDS
        print(end_time.isoformat())
        req = requests.post('http://{}:8080/utilities/water'.format(CENTRAL_DATABASE_HOST),
                            json=result_set_to_influxdb_json(identifying_data, end_time, water_usage))
        if req.status_code >= 400:
            print("ERROR:", req.status_code, req.text)
            return
        simple_logger(beginning_time, end_time, res, water_usage)
        beginning_time = end_time
        end_time = increment(beginning_time)
    print("\n~~~DONE~~~\n")


# Simply increments cur_datetime by QUERY_INTERVAL minutes.
def increment(cur_datetime):
    return cur_datetime + datetime.timedelta(minutes=QUERY_INTERVAL)


# All the data is being read from the database in central time but is displayed as if it is in UTC. All the date and
# time info is in central time, just the timezone tag is in UTC. Don't know, don't care right now. This method converts
# UTC datetime.datetime.now() to central time while keeping the UTC tag. Allows us to compare dates in the database
# to the current time.
def hacky_datetime_now():
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)


# The format to write to CENTRAL_DATABASE in.
def result_set_to_influxdb_json(data, time, water_usage):
    return {
        # "measurement": 'utilities_usage',
        "tags": {
            'id_on_network': data['id_on_network'],
            'home_id': data['home_id'],
            'node_id': data['node_id'],
            'value_id': data['value_id'],
            'manufacturer_id': data['manufacturer_id'],
            'product_id': data['product_id'],
            'label': 'water'
        },
        "timestamp": time.isoformat(),  # The end insert time so we know where to start for the next insertion.
        "fields": {
            'data': water_usage,
            'units': '',
            'type': 'shower',
            'type_val': 1
        }
    }


# A simple logger that uses print statements.
def simple_logger(beginning_time, end_time, res, water_usage):
    print("Beginning time:", beginning_time, "End time:", end_time, "Number data points:", len(res),
          "\tNumber water usage points:", water_usage / GALLONS_PER_15_SECONDS, "Water usage:", water_usage)


# Helper method to either get the first thing in a generator or None.
def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first


if __name__ == '__main__':
    main()
