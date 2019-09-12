import socket
import sys
import struct
import time

UDP_IP = "10.1.137.102"
UDP_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((UDP_IP, UDP_PORT))

sensor_grupo = {
	1:'Whitenoise',
	2:'FlamingoBlack',
	3:'GISSO',
	4:'KOF',
	5:'EQUIPO 404',
	6:'POFFIS'
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

	equipo_sensor = datos[2]
	print("El sensor es del grupo:", sensor_grupo[equipo_sensor])

	seq_sensor = datos[3] + datos[4] + datos[5]
	print("El número de secuencia del sensor es:", seq_sensor)

	tipo = datos[6]
	print("El tipo del sensor es:", tipo_sensor[tipo])

	evento = datos[7]
	if evento:
		print("Hubo evento:", evento)
	else:
		print("No hubo evento:", evento)

	print("-"*30)

def crearPaqueteBuey(random_id,sensor_id):
	sensor_id_data = struct.unpack('BBBB',sensor_id)
	paquete = struct.pack('BBBBB',random_id,sensor_id_data[0],sensor_id_data[1],sensor_id_data[2],sensor_id_data[3])
	print("-"*30)
	print("Enviando respuesta:\n\tRandom ID: ", random_id)
	print("\tEl sensor es del grupo: ", sensor_grupo[sensor_id_data[0]])
	print("\tSecuencia del sensor: ", sensor_id_data[1]+sensor_id_data[2]+sensor_id_data[3])
	print("-"*30)
	
	return paquete


while True:

    data_packed, address = sock.recvfrom(1024)
    paqueteCarreta = struct.unpack('BIBBBBBf', data_packed)
    separarDatos(paqueteCarreta)

    sensor_id = struct.pack('BBBB',paqueteCarreta[2],paqueteCarreta[3],paqueteCarreta[4],paqueteCarreta[5])
    paqueteBuey = crearPaqueteBuey(paqueteCarreta[0],sensor_id)
    sock.sendto(paqueteBuey, address)
