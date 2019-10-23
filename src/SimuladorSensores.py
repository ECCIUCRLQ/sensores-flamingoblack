#import RPi.GPIO as GPIO
import socket
import time
import datetime
import random
import struct
import select
from ipcqueue import sysvmq as SYSV

UDP_IP = "127.0.0.1"
UDP_PORT = 10001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

saved_data = []
last_id = 0

queue_overflow = False
empty_queue = 1

my_queue = SYSV.Queue(63)
my_queue_attributes = my_queue.qattr()
my_queue_max_size = my_queue_attributes['max_bytes']

class myPackage:

	random_id = 0
	date = 0
	sensor_id = bytearray([0x02, 0x00, 0x00, 0x00])
	sensor_type = 0x00
	data = 0.0

my_pack = myPackage()

def randomGenerator():
	
	global last_id
	
	while True:
		my_random = random.randint(0, 255)
		if last_id != my_random:
			last_id = my_random
			return my_random

def randomNumberGenerator(inicio, fin):

	my_random = random.randint(inicio, fin)
	return my_random

def randomFloatGenerator(inicio, fin):

	my_random = random.uniform(inicio, fin)
	return my_random

#switch 
def whitenoise():
	if(my_pack.sensor_id[3] == 0x01):
		my_pack.sensor_type = 0x01
	elif(my_pack.sensor_id[3] == 0x02):
		my_pack.sensor_type = 0x02
	my_pack.data = 1.0

def flamingoblack():
	dato = 1.0
	if(my_pack.sensor_id[3] == 0x01):
		my_pack.sensor_type = 0x01
		my_pack.data = 1.0
	elif(my_pack.sensor_id[3] == 0x02):
		my_pack.sensor_type = 0x03
		if(dato == 1):
			my_pack.data = 0
			dato = 0
		else:
			my_pack.data = 1.0
			dato = 1.0

def gisso():
	if(my_pack.sensor_id[3] == 0x01):
		my_pack.sensor_type = 0x01
	elif(my_pack.sensor_id[3] == 0x02):
		my_pack.sensor_type = 0x04
	my_pack.data = 1.0

def kof():
	if(my_pack.sensor_id[3] == 0x01):
		my_pack.sensor_type = 0x01
	elif(my_pack.sensor_id[3] == 0x02):
		my_pack.sensor_type = 0x05
	my_pack.data = 1.0

def equipo404():
	if(my_pack.sensor_id[3] == 0x01):
		my_pack.sensor_type = 0x01
		my_pack.data = randomFloatGenerator(0.0, 1.0)
	elif(my_pack.sensor_id[3] == 0x02):
		sensorTypeList = [0x06,0x08]
		my_pack.sensor_type = random.choice(sensorTypeList)
		my_pack.data = randomFloatGenerator(0.0, 100.0)

def poffis():
	if(my_pack.sensor_id[3] == 0x01):
		my_pack.sensor_type = 0x09
	elif(my_pack.sensor_id[3] == 0x02):
		my_pack.sensor_type = 0x07
	my_pack.data = randomNumberGenerator(0, 1000)

def generarSensorIdyDato(grupoID):
	switcher = {
		1:whitenoise,
		2:flamingoblack,
		3:gisso,
		4:kof,
		5:equipo404,
		6:poffis
	}
	completarPaquete = switcher.get(grupoID,lambda: "Numero del grupo invalido")
	completarPaquete()

def crearDato():
	my_pack.date = time.time()
	my_pack.random_id = randomGenerator()
	my_pack.sensor_id[0] = randomNumberGenerator(1, 6)
	my_pack.sensor_id[3] = randomNumberGenerator(1, 2)
	generarSensorIdyDato(my_pack.sensor_id[0])
	
	print "\tID Grupo: ", my_pack.sensor_id[0]
	print "\tID Sensor: ", my_pack.sensor_id[3]
	print "\tTipo Sensor: ", my_pack.sensor_type
	print "\tDato: ", my_pack.data

	#my_pack.sensor_type = 0x00

def packageConstructor():
	if my_pack.sensor_type == 9 or my_pack.sensor_type == 7:
		sending_package = struct.pack('BIBBBBBI', my_pack.random_id, my_pack.date, my_pack.sensor_id[0], my_pack.sensor_id[1], my_pack.sensor_id[2], my_pack.sensor_id[3], my_pack.sensor_type, my_pack.data)
	else:
		sending_package = struct.pack('BIBBBBBf', my_pack.random_id, my_pack.date, my_pack.sensor_id[0], my_pack.sensor_id[1], my_pack.sensor_id[2], my_pack.sensor_id[3], my_pack.sensor_type, my_pack.data)
	return sending_package

def checkResponse(data_packed):

	data_unpacked = struct.unpack('BBBBB', data_packed)

	if data_unpacked[0] == my_pack.random_id:
		print("-"*30)
		print("Package was sent and received correctly")
		print("-"*30)
		return 0
	else:
		print("-"*30)
		print("Package was lost")
		print("-"*30)
		return 1

def saveData():

	global saved_data
	global my_queue
	
	saved_data[:] = []
	i = 0

	while i < my_queue.qsize():

		sensor_data = my_queue.get_nowait()
		saved_data.append(sensor_data)
		i += 1

try:
	while True:

		crearDato()
		sending_package = packageConstructor()

		while True:
			sock.sendto(sending_package, (UDP_IP, UDP_PORT))
			timeout = select.select([sock], [], [], 5)

			if timeout[0]:
				data_packed, address = sock.recvfrom(1024)
				package_state = checkResponse(data_packed)

				if package_state == 0:
					break
			else:
				print("Timeout reached. Sending package again.")
			if my_queue_max_size < (my_queue.qsize() + 5):
				saveData()
				queue_overflow = True

		time.sleep(3)
except KeyboardInterrupt:
	print("\nClient shutdown.")
