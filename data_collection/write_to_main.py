from influxdb import InfluxDBClient
import datetime
from dateutil.parser import parse
from threading import Timer
import requests


PERSONAL_DATABASE = 'sterling_ranch'  # The InfluxDB database name to get data from.
CENTRAL_DATABASE = 'utilities_usage'  # The InfluxDB database name to write data to.
CENTRAL_DATABASE_HOST = '18.218.111.49'  # The address of the InfluxDB to write data to.
QUERY_INTERVAL = 60  # How long to wait between writing data to the central database in minutes.
GALLONS_PER_15_SECONDS = 0.425  # Output of our shower. Per 15 seconds due to data being in 15 second intervals.


def main():
    """Calculates the water usage from your personal influxdb and inserts it into the central database every
    QUERY_INTERVAL minutes. It will start transmitting data from the last time you inserted data into the central
    database. If you've never transmitted data before, it will start calculating and transmitting from the start of
    your database.
    This will run every hour on the hour. So if you run it at 5:30 pm, it will automatically run again at 6:00 pm,
    then 7:00 pm, and so on.
    """
    personal_client = InfluxDBClient(database=PERSONAL_DATABASE)
    central_client = InfluxDBClient(host=CENTRAL_DATABASE_HOST, database=CENTRAL_DATABASE)
    q = "select * from water order by desc limit 1"
    last_date_in_central_database = peek(central_client.query(q).get_points())
    if not last_date_in_central_database:  # Run from the start of your database.
        initialize_central_database(personal_client)
    else:  # Run from the last time you transmitted data.
        initialize_central_database(personal_client, last_date_in_central_database['time'])
    # Calculates the amount of time from now to the next hour.
    delay = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1) \
            - datetime.datetime.now() + datetime.timedelta(seconds=1)
    Timer(delay.total_seconds(), main).start()  # Run at the next hour.
    print("Running again at ", datetime.datetime.now() + delay)  # Sanity check.


def initialize_central_database(personal_client, from_datetime=None):
    """Repeatedly makes queries through personal_client and writes the data to central_client starting at from_datetime
    until it reaches the current write interval. The queries are between dates of size QUERY_INTERVAL.
    :param personal_client: The InfluxDB database to get data from.
    :param from_datetime: The last time data was inserted. If None, data will be taken starting from the beginning.
    """
    print("\n~~~INITIALIZING CENTRAL CLIENT FROM {}~~~\n".format(from_datetime if from_datetime else "BEGINNING"))
    q = "select * from value_refresh where label = 'Relative Humidity' limit 1"
    try:
        beginning_time = from_datetime if from_datetime else next(personal_client.query(q).get_points())['time']
    except:
        raise UserWarning("ERROR: NO VALUES IN PERSONAL DATABASE")
    beginning_time = parse(beginning_time).replace(microsecond=0, second=0, minute=0)  # So time across users is synced.
    end_time = increment(beginning_time)
    data = peek(personal_client.query(q).get_points())
    # Now, get and write water usage per QUERY_INTERVAL and data to central_client until the current write interval.
    while end_time < hacky_datetime_now():
        q = "select * from value_refresh where label = 'Relative Humidity' and time >= '{}' and time  < '{}'"\
            .format(beginning_time.isoformat(), end_time.isoformat())
        res = list(personal_client.query(q).get_points())
        # Since data is collected in intervals of 15 seconds, each point that has type_val = 1 represents 1
        # GALLONS_PER_15_SECONDS water used.
        water_usage = sum(data['type_val'] for data in res) * GALLONS_PER_15_SECONDS
        print(end_time.isoformat())
        req = requests.post('http://{}:8080/utilities/water'.format(CENTRAL_DATABASE_HOST),
                            json=result_set_to_influxdb_json(data, end_time, water_usage))
        if req.status_code >= 400:  # Server is not running most likely.
            print("ERROR:", req.status_code, req.text)
            return
        simple_logger(beginning_time, end_time, len(res), water_usage)
        beginning_time = end_time
        end_time = increment(beginning_time)
    print("\n~~~DONE~~~\n")


def increment(cur_datetime):
    """Increments cur_datetime by QUERY_INTERVAL minutes.
    :param cur_datetime: A datetime to be incremented.
    :return: cur_datetime incremented by QUERY_INTERVAL minutes.
    """
    return cur_datetime + datetime.timedelta(minutes=QUERY_INTERVAL)


def hacky_datetime_now():
    """All the data is being read from the database in central time but is displayed as if it is in UTC. All the date
    and time info is in central time, just the timezone tag is in UTC. Don't know, don't care right now. This method
    converts UTC datetime.datetime.now() to central time while keeping the UTC tag. Allows us to compare dates in the
    database to the current time.
    """
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)


def result_set_to_influxdb_json(data, time, water_usage):
    """Converts data to the format to write to CENTRAL_DATABASE in.
    :param data: JSON containing mainly identifying data about the sensor.
    :param time: The end insert time so we know where to start for the next insertion.
    :param water_usage: The amount of water used.
    :return: data formatted to write to CENTRAL_DATABASE.
    """
    return {
        "tags": {
            'id_on_network': data['id_on_network'],
            'home_id': data['home_id'],
            'node_id': data['node_id'],
            'value_id': data['value_id'],
            'manufacturer_id': data['manufacturer_id'],
            'product_id': data['product_id'],
            'label': 'water'
        },
        "timestamp": time.isoformat(),
        "fields": {
            'data': water_usage,
            'units': '',
            'type': 'shower',  # For our purposes, this data always describes whether a shower is on or off.
            'type_val': 1
        }
    }


def simple_logger(beginning_time, end_time, num_instances, water_usage):
    """A simple logger that uses print statements.
    :param beginning_time: The timestamp of the first instance used to write.
    :param end_time: The timestamp of the last instance used to write.
    :param num_instances: Number of instances used.
    :param water_usage: The amount of water used.
    """
    print("Beginning time:", beginning_time, "End time:", end_time, "Number data points:", num_instances,
          "\tNumber water usage points:", water_usage / GALLONS_PER_15_SECONDS, "Water usage:", water_usage)


def peek(iterable):
    """Helper method to get the first item in a generator. This allows us to return None if there is no first item.
    :param iterable: Generator to analyze.
    :return: Either the first element in the generator or None.
    """
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first


if __name__ == '__main__':
    main()
