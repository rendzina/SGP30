#!/usr/bin/python -u
# co2_sgp30.py
# s.hallett 7/2/20
#
# run as python sgp30.py
#
# To run on boot: Service file: /lib/systemd/system/co2.service
# https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
# [Unit]
# Description=CO2  Service
# After=multi-user.target
# [Service]
# Type=idle
# ExecStart=/usr/bin/python /home/pi/sgp30-python/examples/co2_sgp30.py
# WorkingDirectory=/home/pi/sgp30-python/examples
# Restart=always
# RestartSec=10
# User=pi
# [Install]
# WantedBy=multi-user.target
#
# sudo systemctl enable co2.service
# sudo systemctl start co2.service
# sudo systemctl stop co2.service
# systemctl is-active co2.service
#
from sgp30 import SGP30
import os
from datetime import datetime
import threading
import sys
import paho.mqtt.client as mqtt
import json

# Create inherited SPG30 class allowing access to raw values
class SGP30_Raw(SGP30):
  def get_air_quality_raw(self):
        eco2, tvoc = self.command('measure_air_quality')
        return (eco2, tvoc)
######################################################

sgp30 = SGP30_Raw() # SPG30()

THINGSBOARD_HOST = '51.104.217.125' # 'thingsboard.central.cranfield.ac.uk/' # 51.104.217.125
ACCESS_TOKEN = 'sdYU2koQ46RmQ2clmIQv'
INTERVAL = 10

# Prowl #### #######################################
import prowlpy
apikey = 'db7c80d9d3dfff164f9636b3e8f3d8907a6ec2e0'
p = prowlpy.Prowl(apikey)
try:
    p.add('CO2','Starting up',"System commencing", 1, None, "http://www.prowlapp.com/")
    print('Success')
except OSError as err:
    print("OS error: {0}".format(err))
except:
    print("Unexpected error:", sys.exc_info()[0])
#####################################################

# result = sgp30.command('set_baseline', (0xFECA, 0xBEBA))
# result = sgp30.command('get_baseline')
# print(["{:02x}".format(n) for n in result])

sensor_data = {'co2': 0, 'voc': 0}
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
exit_thread = threading.Event()

print("Sensor warming up, please wait...")
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

sgp30.start_measurement(crude_progress_bar)
sys.stdout.write('\n')

client.loop_start()

try:
    while True:
        result = sgp30.get_air_quality()
        raw = sgp30.get_air_quality_raw()
        sensor_data['co2'] = raw[0]
        sensor_data['voc'] = raw[1]
        # debug
        print(datetime.now())
        print(result)
        print(raw)

        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

        # PROWL - Push notifications ######
        #_message = "pm25: %.2f, pm10: %.2f, at %s" % (values[0], values[1], time.strftime("%d.%m.%Y %H:%M:%S"))
        #print(_message)
        try:
            p.add('CO2','Reading', result, 1, None, "http://www.prowlapp.com/")
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
        ###################################

        if exit_thread.wait(timeout=INTERVAL):
            break # https://realpython.com/intro-to-python-threading/
except (KeyboardInterrupt, SystemExit):
    raise

client.loop_stop()
client.disconnect()
# EOF
