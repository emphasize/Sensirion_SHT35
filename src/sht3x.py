#**********************************************************************************#
#
#		SHT3x - Sensirion Temperature Humidity sensor
#
#		Read-out script.
#
#		Olivier den Ouden
#		Royal Netherlands Meterological Institute
#		RD Seismology and Acoustics
#		https://www.seabirdsound.org
#
#**********************************************************************************#

# Modules
import sht3x_main
import smbus2
import time
from numpy import zeros, linspace
import argparse
from argparse import RawTextHelpFormatter
import paho.mqtt.client as mqtt

mqtt_url="address"

# Parser arguments
parser = argparse.ArgumentParser(prog='SHT3x Sensirion Temperature/Humidity sensor Read-out',
    description=('Read-out of the SHT3x Sensirion sensor\n'
    ), formatter_class=RawTextHelpFormatter
)

parser.add_argument(
    '-t', action='store', default=100, type=int,
    help='Time of recording, [sec].\n', metavar='-t')

parser.add_argument(
    '-fs', action='store', default=1, type=int,
    help='Sample rate, [Hz].\n', metavar='-fs')

parser.add_argument(
    '-f', action='store', default=None, type=str,
    help='Filename you want to write it to.\n', metavar='-f')

parser.add_argument('-mqtt', action='store_true',
    help='If you want to send it over mqtt (config needed).\n')

args = parser.parse_args()

fs = args.fs
record_t = args.t
file=args.f
mqtt=args.mqtt
n_samples = record_t*fs

# Check if MS can comunicate with SL
if sht3x_main.init() != True:
    if file:
        with open(file, "w") as file_object:
            line = "Sensor SHT3x Fehler"
            file_object.write(line)
        file_object.close()
    if not mqtt and (file == None):
        print("Sensor SHT3x could not be initialized")
	exit(1)

if mqtt:

    client = mqtt.Client(client_id="",clean_session=True,userdata=None)
    client.username_pw_set(username="user",password="password")
    client.tls_set()
    client.connect(mqtt_url, 1833, 10)

# Save data
Time_array = linspace(0,record_t,n_samples)
Temp = zeros((n_samples,2))
Humi = zeros((n_samples,2))
Temp[:,0] = Time_array[:]
Humi[:,0] = Time_array[:]

# Loop
i = 0
while i < n_samples:
	t_data,h_data = sht3x_main.read()
	Temp[i,1] = t_data
	Humi[i,1] = h_data
	if (t_data != None) and (h_data != None):
		i += 1

		# Print converted data
		read_Humi,read_Temp = sht3x_main.calculation(t_data,h_data)
		if mqtt:
            client.subscribe("topic")
            time.sleep(.5)
			client.publish("topic", read_Humi)
            client.subscribe("topic")
            time.sleep(.5)
			client.publish("topic", read_Temp)
		if file:
			with open(file, "w") as file_object:
				line = "Temp: {:0.2f} C  Hum: {:0.2f} % ".format(read_Temp,read_Humi)
				file_object.write(line)
			file_object.close()
		if not mqtt and (file == None):
			print("Temp: {:0.2f} C  Hum: {:0.2f} % ".format(read_Temp,read_Humi))

		# Sampling rate
		time.sleep(1/fs)
