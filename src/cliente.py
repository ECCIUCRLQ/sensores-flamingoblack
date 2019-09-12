import socket
import sys
import struct
import random
import time
import select

UDP_IP = "127.0.0.1"
UDP_PORT = 10001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

def randomGenerator():

	my_random = random.randint(0, 255)
	return my_random

class protocoloComun:

	random_id = randomGenerator()
	date = int(time.time())
	sensor_id = bytearray([0x01, 0x00, 0x00, 0x02])
	sensor_type = 0x01
	data = 1.4878

my_protocol = protocoloComun()
sending_package = struct.pack('BIBBBBBf', my_protocol.random_id, my_protocol.date, my_protocol.sensor_id[0],
				my_protocol.sensor_id[1], my_protocol.sensor_id[2], my_protocol.sensor_id[3],
				my_protocol.sensor_type, my_protocol.data)

timeouts = 0

while True:
	sock.sendto(sending_package, (UDP_IP, UDP_PORT))
	timeout = select.select([sock], [], [], 5)
	if timeouts == 3:
		print("Server not responding.")
		exit()
	elif timeout[0]:
		data_packed, address = sock.recvfrom(1024)
		data_unpacked = struct.unpack('BBBBB', data_packed)
		break
	else:
		timeouts += 1
		print("Timeout reached. Sending package again.")

if data_unpacked[0] == my_protocol.random_id:
	print("-"*30)
	print("Packet was sent and received correctly")
	print("-"*30)
else:
	print("-"*30)
	print("Packet was lost")
	print("-"*30)
