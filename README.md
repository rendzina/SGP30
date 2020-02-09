# SGP30 CO2 and VOC Sensing with A Raspberry Pi
 This Git describes code to capture and retransmit CO<sub>2</sub> and VOC (Volatile Organic Compounds) measurements from a [SGP30](https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Gas/Sensirion_Gas_Sensors_SGP30_Datasheet.pdf) sensor on a Raspberry Pi to a remote dashboard in [ThingsBoard](https://thingsboard.io/) on a Raspberry Pi. As a further capability, the 'Push Notification' service 'Prowl' was used to send a debug data stream to an Apple device.

 ![Raspberry Pi and SGP30 sensor](https://github.com/rendzina/sgp30/blob/master/images/PI_and_SGP30_thmb.jpeg "Raspberry Pi and SGP30 sensor")

 ## Project
 This project uses a Raspberry Pi to run an attached SGP30 sensor, able to record CO<sub>2</sub> and VOC levels, and for it to run unattended (no attached keyboard/mouse). Data then uploaded into a dashboard in [ThingsBoard](https://thingsboard.io/).

 The project uses a Raspberry Pi (we used a Pi 4, although any model Pi should do),
 ## Hardware
 The following hardware is used:
 - [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)

 The Pi was updated and patched to the latest level before use:
 ```
 sudo apt-get update
 sudo apt-get upgrade
 ```
 Raspi-config was used to enable I2C, and 'ssh' (the way we accessed it), and for it to boot up in command line mode.

 - [SGP30 Air Quality Sensor Breakout](https://shop.pimoroni.com/products/sgp30-air-quality-sensor-breakout)

 The first step was to solder a pin connector to the Pi Moroni breakout board. The sensor pinout of the Pi Moroni breakout device unfortunately is not directly pin compatible with the GPIO bus pinout of the Pi. The solution however is just to use four connecting wires between the sensor and the Pi's [GPIO bus](https://www.raspberrypi.org/documentation/usage/gpio/) and join the two up appropriately. Note that by contrast, the SGP30 Breakout board from [Adafruit](https://www.adafruit.com/product/3709) does appear to be pin compatible. The four connections needed are:
 ```
 SGP Breakout         Raspberry Pi
 Connection           GPIO pin Connection
 2.6v   ------------  3v3 power (pin 1)
 SDA    ------------  GPIO2 SDA (pin 2)
 SCL    ------------  GPIO2 SCL (pin 3)
 0
 GND    ------------  Ground (pin 9)
 ```
 ![Raspberry Pi and SGP30 sensor wiring](https://github.com/rendzina/sgp30/blob/master/images/SGP30_Wiring_thmb.jpeg "Raspberry Pi and SGP30 sensor wiring")

 ## Software
 Pi Moroni provide an excellent [Python library](https://github.com/pimoroni/sgp30-python) to run a SGP30. This was installed on the Pi

 Pi Moroni provide two methods to install the software, we found the method that worked the best was:
```
git clone https://github.com/pimoroni/sgp30-python
cd sgp30-python
sudo ./install.sh
```
On installing we initially encountered the error: *ImportError: cannot import name ‘SGP30’ from ‘sgp30’*. It seems we are not alone and others have also [experienced this error](https://forums.pimoroni.com/t/importerror-cannot-import-name-sgp30-from-sgp30/12261). We had to completely uninstall the library (pip and pip3), then reinstall as above (a few times) before it worked.
```
pip uninstall SGP30
pip3 uninstall SGP30
```

 ## Code
 The code ['Temperature upload over MQTT using Raspberry Pi and DHT22 sensor'](https://thingsboard.io/docs/samples/raspberry/temperature/) was used as a starting point.

 The code was adapted to work with the Pi Moroni SGP30 library, see the file 'co2_sgp30.py'. A number of adaptations were made:

 1. The PiMoroni SGP30 library uses Python class 'SGP30'. When this is instanced in the code, the function sgp30.get_air_quality() is called to output readings. The readings are fully text formatted and so are suitable for printing out - but the class does not offer access to the raw underlying data. We therefore created an *inherited class* in the Python, and added a new function to return the raw data as we required, thus:
 ```
 class SGP30_Raw(SGP30):
   def get_air_quality_raw(self):
         eco2, tvoc = self.command('measure_air_quality')
         return (eco2, tvoc)
```
The sensor_data list was used to collect the CO<sub>2</sub> and VOC data before it was sent to ThingsBoard in [JSON](https://docs.python.org/3/library/json.html) form.

2. The code to run the *'endless loop'*, taking a reading every so many seconds ('INTERVAL') originally used time.sleep(). We did not prefer this, as 'time.sleep()' can be very CPU intensive, so an alternative 'threading' loop approach was used, based on the great examples [here](https://realpython.com/intro-to-python-threading/).

 ### Running at Start-Up
 To run the code at startup, a service was created, 'co2.service'. Copying this file over to the home folder on the pi, the service was then placed into '/lib/systemd/system/'.
 ```
 sudo cp co2.service /lib/systemd/system
 ```
 The new service can then be started, stopped and automated thus:
 ```
 sudo systemctl start co2.service
 sudo systemctl stop co2.service
 sudo systemctl enable co2.service
 systemctl status co2.service
 ```

 ## Instructions
 The code can be run initially in testing as:
 ```
 cd /sgp30-python/examples
 python sgp30.py
 ```

 Once the code was known to work correctly, the Pi could be rebooted, and the service 'co2', described above, started to run the code automatically.

 ## ThingsBoard
 [ThingsBoard](https://thingsboard.io/) offers *'Device management, data collection, processing and visualization for your IoT solution'*. We were working with our own installation of ThingsBoard.

 In ThingsBoard, we added a new 'SGP30' device and obtained its access token. This was copied to the ACCESS_TOKEN field in the Python code.

 Next a new dashboard was created, and an alias added to link to the new device. Then the dashboard was laid out with a number of Widgets to visualise the data.

 ![dashboard](https://github.com/rendzina/sgp30/blob/master/images/sgp30_dashboard.png "SGP30 ThingsBoard dashboard")

 ## Prowl
 [Prowl](https://www.prowlapp.com) is a push notification client for iOS, allowing push to your iPhone, iPod touch, or iPad notifications from another source. Here we used [Pyprowl](https://pypi.org/project/pyprowl/) to allow Prowl notifications from within Python. With Pyprowl installed, code was added in Python to enable sending the fully formatted sensor output as a notification.

 ![Prowl](https://github.com/rendzina/sgp30/blob/master/images/prowl_ios_notification_thmb.jpg "Prowl notification")

 ## Observations
 The Rasberry Pi code here uses the amazing SGP30 breakout board to capture a stream of CO<sub>2</sub> and VOC readings. These are passed to a ThingsBoard dashboard for display, and Prowl for push notification - IoT in action!.
