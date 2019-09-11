import socket
import sys
import struct
import random
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def randomGenerator():

	my_random = random.randint(0, 65535)
	return my_random

class protocoloComun:

	random_id = randomGenerator()
	date = int(time.time())
	sensor_id = bytearray([0x01, 0x00, 0x00, 0x02])
	sensor_type = 0x01
	data = 0x00

my_protocol = protocoloComun()
sending_package = struct.pack('Hibbbbbb', my_protocol.random_id, my_protocol.date, my_protocol.sensor_id[0],
						my_protocol.sensor_id[1], my_protocol.sensor_id[2], my_protocol.sensor_id[3],
						my_protocol.sensor_type, my_protocol.data)

sock.sendto(sending_package, (UDP_IP, UDP_PORT))

data_packed, address = sock.recvfrom(1024)
data_unpacked = struct.unpack('Hbbbb', data_packed)

if data_unpacked[0] == my_protocol.random_id:
	print("-"*30)
	print("Packet was sent and received correctly")
	print("-"*30)
else:
	print("-"*30)
	print("Packet was lost")
	print("-"*30)