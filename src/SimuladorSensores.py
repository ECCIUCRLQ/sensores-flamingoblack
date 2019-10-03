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

#buzon = SYSV.Queue(63)

class myPackage:

	random_id = 0
	date = 0
	sensor_id = bytearray([0x02, 0x00, 0x00, 0x00])
	sensor_type = 0x00
	data = 0.0

my_pack = myPackage()

def randomNumberGenerator(inicio, fin):

	my_random = random.randint(inicio, fin)
	return my_random

def randomFloatGenerator(inicio, fin):

	my_random = random.uniform(inicio, fin)
	return my_random

def crearDato():
	my_pack.date = time.time()
	my_pack.random_id = randomNumberGenerator(0, 255)
	my_pack.sensor_id[0] = randomNumberGenerator(1, 6)
	my_pack.sensor_id[3] = randomNumberGenerator(1, 2)
	my_pack.sensor_type = randomNumberGenerator(1, 9)
	if my_pack.sensor_type == 9 or my_pack.sensor_type == 7:
		my_pack.data = randomFloatGenerator(0, 1000)
	elif my_pack.sensor_type == 6 or my_pack.sensor_type == 8:
		my_pack.data = randomFloatGenerator(0.0, 100.0)
	else:
		my_pack.data = randomFloatGenerator(0.0, 1.0)

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
