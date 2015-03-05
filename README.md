Newport's Omega
===============

The content of this repository has been prepared to control a [Newport's 
instrument](http://www.newportus.com/ppt/INFS.html) to measure strain gage. 
It would be extended to other instruments from the same series that have the 
same way to control.

This code can be found in two (mirrored) locations, in [github](https://github.com/srgblnch/NewportOmega)
 as a repository and in [sourceforge](https://sourceforge.net/p/tango-ds/code/HEAD/tree/DeviceClasses/MeasureInstruments/NewportOmega/)
 as a subdirectiory of tango-ds project.

 In the *src* directory there is a basic file called *OmegaCommunications.py*. 
 This is the main file that supports the communications with the instrument 
 and encapsulates the different methods to connect. By now it requires 
 [tausus](https://www.taurus-scada.org/), but this may change in a short 
 future to minimise the dependencies.
 
 Apart from this file, there is another called *newportomega.py* that 
 has been generated by [pogo](http://www.esrf.eu/computing/cs/tango/tango_doc/tools_doc/pogo_doc/)
 and its methods has been adjusted to use the class in the previous mentioned
 file (*OmegaCommunications.py*) to thurst the readings into an instance on 
 the tango control system.
 
Usage
-----
 
 Stand alone use can be made by command line calls of the 
 *OmegaCommunications.py* file:
```
$ python OmegaCommunications.py -h
Usage: OmegaCommunications.py [options]

Options:
  -h, --help            show this help message and exit
  -s SERIAL, --serial=SERIAL
                        String with the reference name to use for serial line
                        connection.
  -a ADDRESS, --address=ADDRESS
                        Two digit string with the address of the OMEGA.
  -t SLEEP, --sleep=SLEEP
                        Wait time between write and read operations
  --log-level=LOG_LEVEL
                        Define the logging level to print out. Allowed values
                        error|warning|info|debug, being info the default
  -r READS, --reads=READS
                        Number of consecutive sets of readings
```

An execution example can be:

```
$ python OmegaCommunications.py -s /dev/ttyr00 -a 01 -t 0.1 --log-level=Debug
MainThread     DEBUG    2014-12-23 11:59:39,416 OMEGA: sending: '*01X01\r'
MainThread     DEBUG    2014-12-23 11:59:39,665 OMEGA: received ''
MainThread     DEBUG    2014-12-23 11:59:39,916 OMEGA: received '01X01090.252\r'
MainThread     DEBUG    2014-12-23 11:59:39,916 OMEGA: Answer string: '090.252'
MainThread     DEBUG    2014-12-23 11:59:39,917 OMEGA: sending: '*01X02\r'
MainThread     DEBUG    2014-12-23 11:59:40,169 OMEGA: received ''
MainThread     DEBUG    2014-12-23 11:59:40,421 OMEGA: received '01X02090.378\r'
MainThread     DEBUG    2014-12-23 11:59:40,421 OMEGA: Answer string: '090.378'
MainThread     DEBUG    2014-12-23 11:59:40,422 OMEGA: sending: '*01X03\r'
MainThread     DEBUG    2014-12-23 11:59:40,672 OMEGA: received ''
MainThread     DEBUG    2014-12-23 11:59:40,924 OMEGA: received '01X03069.042\r'
MainThread     DEBUG    2014-12-23 11:59:40,925 OMEGA: Answer string: '069.042'
MainThread     DEBUG    2014-12-23 11:59:40,925 OMEGA: sending: '*01X04\r'
MainThread     DEBUG    2014-12-23 11:59:41,176 OMEGA: received ''
MainThread     DEBUG    2014-12-23 11:59:41,429 OMEGA: received '01X04090.313\r'
MainThread     DEBUG    2014-12-23 11:59:41,429 OMEGA: Answer string: '090.313'
read: 1/1
Unfiltered Value: 90.252
Filtered:         90.313
Peak:             90.378
Valley:           69.042
```

With this command it has been used a tty file (in this case a 
[moxa](http://www.moxa.com/product/NPort_6450.htm) remote port but a subdevice 
from tango can be used. From the serial line device server currently available 
options it has been tested using the 
[PySerial](http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/Communication/PySerial/index.html)
 but the *C++* option for 
 [serial](http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/Communication/SerialLine/index.html)
 communication will be supported also in a near future.

### Tango device server

About the other important file, the *newportomega.py*, it can be 
launched having a tango control system middleware infrastructure installed.

For such thing, a new device server instance has to be created and the device 
that will be in charge of this instrument in the distributed control system 
requires a few properties.

  * Serial: (Mandatory) String with the reference name to use for serial 
  line connection.
  * Address: (if required) Two digit string with the address of the OMEGA.
  * Measures: List of elements to read from the instrument: UnfilteredValue, 
  FilteredValue, PeakValue, ValleyValue.

With this last property, dynamic attributes will be created for each of the 
measurements that are requested to made by the instrument

Wish list
---------

By now only the state and the status have events. In a near future all the 
measure attributes shall have also. This will require a reading loop to the 
instrument that will manage the reading period to avoid stress the instrument.

As mention before, it's also in this list the support to the *C++ Serial* 
tango device server.

The dependency to *taurus* for logging, shall be changed to *tango* logging 
to reduce dependency. And wouold be good to have an stand alone alternative if 
it's tango what is not installed.

Extend the commands supported to communicate with the instrument.

Test and extend reliability and error messaging using the device status 
string message.

Qualities to the attributes. Like changing when readings changes above the 
noise (noise definition required).

Measurement units to the Tango attributes.
