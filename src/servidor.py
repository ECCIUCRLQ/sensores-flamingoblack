import socket
import sys
import struct
import time
from ipcqueue import sysvmq as SYSV

UDP_IP = "10.1.137.192"
UDP_PORT = 10002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

buzon = SYSV.Queue(14)
paquetes_recibidos = []


sensor_grupo = {
	1: 'Whitenoise',
	2: 'FlamingoBlack',
	3: 'GISSO',
	4: 'KOF',
	5: 'EQUIPO 404',
	6: 'POFFIS'
}

tipo_sensor = {
	0: 'Keep Alive',
	1: 'Movimiento',
	2: 'Big Sound',
	3: 'Fotoresistor',
	4: 'Shock',
	5: 'Touch',
	6: 'Humedad',
	7: 'Big Sound',
	8: 'Temperatura',
	9: 'Ultrasonico'
}

def crearPaqueteBuey(random_id,sensor_id):

	sensor_id_data = struct.unpack('BBBB',sensor_id)
	paquete = struct.pack('BBBBB',random_id,sensor_id_data[0],sensor_id_data[1],sensor_id_data[2],sensor_id_data[3])
	print "Enviando respuesta:\n\tRandom ID: ", random_id
	print "\tEl sensor es del grupo: ", sensor_grupo[sensor_id_data[0]]
	print "\tSecuencia del sensor: ", sensor_id_data[1]+sensor_id_data[2]+sensor_id_data[3]
	print(" ")

	return paquete

def pasarDatosAlBuzon(paquete):

	buzon.put([paquete[2],paquete[3],paquete[4],paquete[5],paquete[1],paquete[7]], block=True )

	print "Mensaje con datos recibido.\nEnviado a la interfaz para ser almacenada."
	print "Sensor de tipo: ", tipo_sensor[paquete[6]]
	print "Dato: ", paquete[7]
	print("-"*30)

def esKeepAlive(tipo):
		if(tipo):
			return False
		else:
			return True

def desempacarFloat_o_Int(data_packed):
	paquete = struct.unpack('BIBBBBBf', data_packed)
	if(paquete[6] == 0x07 or paquete[6] == 0x09):
		paquete = struct.unpack('BIBBBBBi', data_packed)
	elif(paquete[6] == 0x06 or paquete[6] == 0x08):
		paquete = struct.unpack('BIBBBBBf', data_packed)
	else:
		datoByte = bytearray(1)
		if(paquete[7]):
			datoByte[0] = 0x01
		else:
			datoByte[0] = 0x00
		nuevoPaquete = struct.pack('BIBBBBBB', paquete[0],paquete[1],paquete[2],paquete[3],paquete[4],paquete[5],paquete[6],datoByte[0])
		paquete = struct.unpack('BIBBBBBB', nuevoPaquete)

	print ("-"*30)
	print "Paquete recibido, desempacando..."
	print (" ")

	return paquete

try:
	while True:

		data_packed, address = sock.recvfrom(1024)
		paqueteCarreta = desempacarFloat_o_Int(data_packed)

		sensor_id = struct.pack('BBBB',paqueteCarreta[2],paqueteCarreta[3],paqueteCarreta[4],paqueteCarreta[5])
		paqueteBuey = crearPaqueteBuey(paqueteCarreta[0],sensor_id)
		sock.sendto(paqueteBuey, address)

		if (paqueteBuey in paquetes_recibidos):
			print "El paquete recibido con random ID ", paqueteCarreta[0] ," del equipo ", sensor_grupo[paqueteCarreta[2]] ," esta repetido, este sera descartado."
		else:
			if(esKeepAlive(paqueteCarreta[6])):
				seq = paqueteCarreta[3]+paqueteCarreta[4]+paqueteCarreta[5]
				print "Paquete Keep Alive recibido."
				print ("-"*30)
			else:
				pasarDatosAlBuzon(paqueteCarreta)

		if(len(paquetes_recibidos) <= 5):

			paquetes_recibidos.insert(0,paqueteBuey)
		else:
			paquetes_recibidos.pop(5)
			paquetes_recibidos.insert(0,paqueteBuey)
except KeyboardInterrupt:
	print("\nEl usuario ha cerrado el servidor")
