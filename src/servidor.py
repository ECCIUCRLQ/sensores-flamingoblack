import socket
import sys
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((UDP_IP, UDP_PORT))

sensor_grupo = {
	1:'Whitenoise',
	2:'FlamingoBlack',
	3:'GISSO',
	4:'KOF',
	5:'EQUIPO 404'
}

tipo_sensor = {
	0:'Keep Alive',
	1:'Movimiento',
	2:'Big Sound',
	3:'Fotoresistor',
	4:'Shock',
	5:'Touch',
	6:'Humedad/Temperatura'
}

def separarDatos(datos):

	print("-"*30)

	random_id = datos[0]
	print("El random_id es:", random_id)

	fecha = time.ctime(datos[1])
	print("Local time:", fecha)

	sensor_id = datos[2]
	print("El sensor es del grupo:", sensor_grupo[sensor_id])

	seq_sensor = datos[3] + datos[4] + datos[5]
	print("El número de secuencia del sensor es:", seq_sensor)

	tipo = datos[6]
	print("El tipo del sensor es:", tipo_sensor[tipo])

	evento = datos[7]
	if evento:
		print("Hubo evento")
	else:
		print("No hubo evento")

	print("-"*30)


while True:

    data_packed, address = sock.recvfrom(1024)
    data_unpacked = struct.unpack('Hibbbbbb', data_packed)
    separarDatos(data_unpacked)

    answer_package = struct.pack('Hbbbb', data_unpacked[0], data_unpacked[2], data_unpacked[3], data_unpacked[4], data_unpacked[5])
    sock.sendto(answer_package, address)