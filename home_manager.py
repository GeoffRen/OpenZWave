import csv
import signal
import time
from openzwave.command import ZWaveNodeSensor
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from pydispatch import dispatcher
from influxdb import InfluxDBClient
from threading import Timer


DATABASE = 'sterling_ranch'
TIME_INTERVAL = 15


def ozw_debug(logger, network):
    logger.info("------------------------------------------------------------")
    logger.info("Use openzwave library : {}".format(network.controller.ozw_library_version))
    logger.info("Use python library : {}".format(network.controller.python_library_version))
    logger.info("Use ZWave library : {}".format(network.controller.library_description))
    logger.info("Network home id : {}".format(network.home_id_str))
    logger.info("Controller node id : {}".format(network.controller.node.node_id))
    logger.info("Controller node version : {}".format(network.controller.node.version))
    logger.info("Nodes in network : {}".format(network.nodes_count))
    logger.info("------------------------------------------------------------")


def value_refresh_to_influxdb_json(node, val):
    return [{
        "measurement": "value_refresh",
        "tags": {
            'id_on_network': val.id_on_network,
            'home_id': node.home_id,
            'node_id': node.node_id,
            'value_id': val.value_id,
            'manufacturer_id': node.manufacturer_id,
            'product_id': node.product_id,
            'label': str(val.label),
        },
        "time": time.asctime(time.localtime()),
        "fields": {
            'data': str(val.data_as_string),
            'units': str(val.units),
            'type': 'none'
        }
    }]


class HomeManager(object):
    def __init__(self, device_path, ozw_log_level, logger):
        self.logger = logger

        options = ZWaveOption(device_path,
                              config_path="./venv/lib/python3.6/site-packages/python_openzwave/ozw_config",
                              user_path=".", cmd_line="")
        options.set_log_file("OZW.log")
        options.set_append_log_file(False)
        options.set_save_log_level(ozw_log_level)
        options.set_console_output(False)
        options.set_logging(True)
        options.lock()
        self.options = options
        self.network = ZWaveNetwork(options, log=None, autostart=False)
        self.csvfile = open('output.csv', 'a')
        self.writer = csv.writer(self.csvfile)
        self.client = InfluxDBClient(database=DATABASE)

    def start(self):
        self.logger.info("Starting network...")
        self.network.start()

    def stop_signal(self, signum, frame):
        self.stop()

    def stop(self):
        self.logger.info("Stopping network...")
        self.network.stop()
        self.csvfile.close()
        self.logger.info("Stopped")

    def connect_signals(self):
        dispatcher.connect(self.signal_network_ready, self.network.SIGNAL_NETWORK_READY)
        signal.signal(signal.SIGINT, self.stop_signal)

    # Note -- the name of the network parameter must not change!
    def signal_network_ready(self, network):
        if self.network is not network:
            return
        else:
            del network
        ozw_debug(self.logger, self.network)
        self.logger.info("Network is ready!")
        self.start_polling()

    @staticmethod
    def is_sensor(node):
        return isinstance(node, ZWaveNodeSensor) and not len(node.get_sensors()) is 0

    def start_polling(self):
        Timer(TIME_INTERVAL, self.start_polling).start()
        labels_to_be_polled = {'Luminance', 'Relative Humidity', 'Temperature', 'Ultraviolet', 'Alarm Level', 'Burglar'}
        for node_id, node in self.network.nodes.items():
            if self.is_sensor(node):
                for val_id in self.network.nodes[node_id].values:
                    val = self.network.nodes[node_id].values[val_id]
                    if val.label in labels_to_be_polled:
                        self.logger.info("Received value refresh %s: %s", val.id_on_network, val)
                        self.client.write_points(value_refresh_to_influxdb_json(node, val))
