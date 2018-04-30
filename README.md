# personal_backend for each linux box in each Sterling Ranch home
## NOTE: Source code for things described here are in data_collection. shower_analysis contains machine learning experiments.

This program initializes the ZWave Network, logging Alarm Level, Burglar, Ultraviolet, Luminance, Relative Humidity, and Temperature readings to an influxdb instance every 15 seconds.
It also contains a script that can set the 'type' of all datapoints between two times in the influxdb instance to 'shower' and a script that finds your total water usage per some amount of time and transmits that data to a central influxdb on an aws instance. Note that write_to_main.sh will run automatically once every hour once you start it.

## Set-up

### Ubuntu (also Windows Subsystem for Linux with Ubuntu)

* ./setup_ubuntu.sh
* ./allow_port_access_forever_ubuntu.sh

### OS X

* ./setup_os_x.sh

## Running main script

* ./run.sh <optional port name, defaults to /dev/cu.usbmodem1411 for my mac>

## Running shower update script

* ./shower_labeller.sh <beginning time eg 8:43:20pm> <ending time eg 8:55:34pm>

## Running data transmitter script

* ./write_to_main.sh

## Stopping
* Just do ctrl+C once, it will stop itself.

## FAQ

### What configurations do I need to make?
-Change the DEVICE_PATH variable in the Config class in main.py to the serial port your zwave stick is in.

-Either create a influxdb database named 'sterling_ranch' or change the DATABASE variable in home_manager.py, shower_labeller.py, and write_to_main.py (PERSONAL_DATABASE instead of DATABASE) to be whatever you name your database.

-Change GALLONS_PER_15_SECONDS to be your personal shower head rate in write_to_main.py.

-If you want to write your filtered data to a influxdb instance on your personal machine, change CENTRAL_DATABASE to whatever you name your influxdb instance and CENTRAL_DATABASE_HOST to localhost.

-CONFIG_NUMBER in home_manager.py may need to change. This config number may be unique according to each sensor. This config number corresponds to the group 1 update interval config for your Aeotec Multisensor 6. To find this, I just listed out all the different configs in my sensor and then looked for it. Contact me if you do not know how to do this.

### What should the port name be?

**Let # as used below to be the port number of the ZWave Stick.**

#### Windows Subsystem for Linux with Ubuntu
It should be COM# in Windows and /dev/ttyS# in Ubuntu. You can try figure out what # is by opening Device Manager and looking at the USB devices list, then trying each with `./run.sh /dev/ttyS#` until it works. If you get an error message that permission is denied, run `./allow_port_access_once.sh /dev/tty/S#`.

#### OS X
My left port on a 2013 Macbook Pro on 10.13.4 is named /dev/cu.usbmodem1411.
Turns out cu should be used instead of tty for some reason.

#### Any other Linux system
It should be /dev/ttyACM#, you may need permission to read/write to the port. In that case, run `./allow_port_access_once.sh /dev/ttyACM#` or use the indefinite version.

### Is it relatively safe to delete all the files that seem to be generated (i.e. pyozw.sqlite) when I run the sniffer?
Yes, just make sure you stop the sniffer first.

### How do I install influxdb?
Follow the instructions on https://docs.influxdata.com/influxdb/v0.9/introduction/installation/
Then create a database named 'sterling_ranch'.

### How do I get fancy graphs for my data?
Download grafana following instructions on http://docs.grafana.org/installation/ 
After starting grafana, go to the gui on localhost:3000 and login with username 'admin' and pwd 'admin' (the defaults).
Now you can create your graphs!
