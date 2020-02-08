#!/usr/bin/python -u
# co2_sgp30.py
#
# run as python sgp30.py
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

THINGSBOARD_HOST = 'IP NUMBERS GO HERE' # Add here the Thingsboard server IP, eg. 123.456.789.101
ACCESS_TOKEN = 'TOKEN GOES HERE' # Add here the THingsBoard device token, eg. abcDEF123ghiJKL456
INTERVAL = 10

# Prowl #### #######################################
import prowlpy
apikey = 'PROWL TOKEN GOES HERE' # Add Prowl token here, eg. aaaaabbbbbccccccddddddeeee
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
        try:
            p.add('CO2','Reading', result, 1, None, "http://www.prowlapp.com/")
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
        ###################################

        if exit_thread.wait(timeout=INTERVAL):
            break # see https://realpython.com/intro-to-python-threading/
except (KeyboardInterrupt, SystemExit):
    raise

client.loop_stop()
client.disconnect()
# EOF
