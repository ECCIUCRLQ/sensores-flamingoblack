import socket
import sys
import struct
import random
import time
import select
from ipcqueue import sysvmq as SYSV

UDP_IP = "127.0.0.1"
UDP_PORT = 10001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)
buzon = SYSV.Queue(63)
emptyQueue = 1

class myPackage:

	random_id = 0
	date = 0
	sensor_id = bytearray([0x02, 0x00, 0x00, 0x00])
	sensor_type = 0x00
	data = 0

my_pack = myPackage()

def packageConstructor():

	sending_package = struct.pack('BIBBBBBi', my_pack.random_id, my_pack.date, my_pack.sensor_id[0], my_pack.sensor_id[1], my_pack.sensor_id[2], my_pack.sensor_id[3], my_pack.sensor_type, my_pack.data)
	return sending_package

def randomGenerator():

	my_random = random.randint(0, 255)
	return my_random

def obtainDateData():

	try:
		sensor_data = buzon.get_nowait()
	except:
		print("Queue is empty")
		global emptyQueue
		emptyQueue = 1
		return

        if sensor_data[1] == 1:
                global emptyQueue
                emptyQueue = 0
                if(sensor_data[0]==2):
                    my_pack.sensor_type = 0x00
                else:
                    my_pack.sensor_type = 0x01
                my_pack.data = sensor_data[0]
                my_pack.date = sensor_data[2]
                my_pack.sensor_id[3] = 0x01
                my_pack.random_id = randomGenerator()
        elif sensor_data[1] == 2:
                global emptyQueue
                emptyQueue = 0
                if(sensor_data[0]==2):
                    my_pack.sensor_type = 0x00
                else:
                    my_pack.sensor_type = 0x03
                my_pack.data = sensor_data[0]
                my_pack.date = sensor_data[2]
                my_pack.sensor_id[3] = 0x02
                my_pack.random_id = randomGenerator()


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
    
    obtainDateData()
    if emptyQueue == 0:      
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
    time.sleep(0.5)
