# personal_backend for each linux box in each Sterling Ranch home

This program initializes the ZWave Network, logging Alarm Level, Burglar, Ultraviolet, Luminance, Relative Humidity, and Temperature readings to an influxdb instance every 15 seconds.
It also contains a script that can set the 'type' of all datapoints between two times in the influxdb instance to 'shower'.

## Set-up

### Ubuntu (also Windows Subsystem for Linux with Ubuntu)

* ./setup_ubuntu.sh
* ./allow_port_access_forever_ubuntu.sh

### OS X

* ./setup_os_x.sh

## Running main script

* ./run.sh <optional port name, defaults to /dev/ttyACM0 for Linux>

## Running shower update script

* ./shower_labeller.sh <beginning time eg 8:43:20pm> <ending time eg 8:55:34pm>

## Stopping
* Just do ctrl+C once, it will stop itself.

## FAQ

### What configurations do I need to make?
-Change the DEVICE_PATH variable in the Config class in main.py to the serial port your zwave stick is in.

-Either create a influxdb database named 'sterling_ranch' or change the DATABASE variable in home_manager.py and shower_labeller.py to be whatever you name your database.

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
