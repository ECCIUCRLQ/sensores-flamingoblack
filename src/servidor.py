import socket
import sys
import struct
import time
from ipcqueue import sysvmq as SYSV

UDP_IP = "127.0.0.1"
UDP_PORT = 10001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

buzon = SYSV.Queue(36)
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
	6: 'Humedad/Temperatura'
}

"""
def separarDatos(datos):

	print("-"*30)

	random_id = datos[0]
	print("El random_id es:", random_id)

	fecha = time.ctime(datos[1])
	print("Local time:", fecha)

	equipo_sensor = datos[2]
	print("El sensor es del grupo:", sensor_grupo[equipo_sensor])

	seq_sensor = datos[3] + datos[4] + datos[5]
	print("El numero de secuencia del sensor es:", seq_sensor)

	tipo = datos[6]
	print("El tipo del sensor es:", tipo_sensor[tipo])

	evento = datos[7]
	if evento:
		print("Hubo evento:", evento)
	else:
		print("No hubo evento:", evento)

	print("-"*30)

"""

def crearPaqueteBuey(random_id,sensor_id):

	sensor_id_data = struct.unpack('BBBB',sensor_id)
	paquete = struct.pack('BBBBB',random_id,sensor_id_data[0],sensor_id_data[1],sensor_id_data[2],sensor_id_data[3])
	print "Enviando respuesta:\n\tRandom ID: ", random_id 
	print "\tEl sensor es del grupo: ", sensor_grupo[sensor_id_data[0]] 
	print "\tSecuencia del sensor: ", sensor_id_data[1]+sensor_id_data[2]+sensor_id_data[3] 
	print(" ")

	return paquete

def pasarDatosAlBuzon(paquete):

	#datos_sensores = struct.pack('IBBBBBf',paquete[1],paquete[2],paquete[3],paquete[4],paquete[5],paquete[6],paquete[7])
	buzon.put([paquete[1],paquete[2],paquete[3],paquete[4],paquete[5],paquete[6],paquete[7]], block=True)

        seq = paquete[3] + paquete[4] + paquete[5]
	print "Mensaje con datos recibido.\nEnviado al interpretador."
	print("-"*30)

def esKeepAlive(tipo):
		if(tipo):
			return False
		else:
			return True

def desempacarFloat_o_Int(data_packed):
	paquete = struct.unpack('BIBBBBBi', data_packed)
	if(paquete[6] == 0x06 or paquete[6] == 0x08):
		paquete = struct.unpack('BIBBBBBf', data_packed)
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
	buzon.close()
	print("\nEl usuario ha cerrado el servidor")
