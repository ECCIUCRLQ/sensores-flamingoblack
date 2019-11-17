# coding=utf-8
import time
import os
import socket
import struct
import uuid
import threading
import manejadorPaquetes as manepack

class interfazDistribuida:

	def __init__(self):

		# Hash que mantiene los metadatos de los nodos
		# nodo: [ip, espacio disponible]
		# ejemplo 1: [21581, 100]
		self.node_manager = {

		}

		# Hash que crecera a medida que lleguen paginas, se asocia pagina:nodo
		self.page_manager = {

		}

		# La ip va a estar quemada, se quema el día de la demo
		self.active = False
		self.status = False
		self.my_ip = "127.0.0.1"
		self.my_broadcast_port = 6666
		self.my_tcp_port = 3114
		self.mac_addres_in_bytes = uuid.getnode().to_bytes(6, 'little')
		self.raw_mac_address = uuid.getnode()
		self.round = 0
		self.nodeCounter = 0

	# ------------------
	# Método que busca por best-fit cuál nodo es el más adecuado y guarda página
	# ------------------

	def save_data(self, package):

		minimum_available = 100000000
		which_node = 0
		
		for key in self.node_manager:
			
			node_data = self.node_manager[key]
			
			if minimum_available > node_data[1] and node_data[1] > len(package[2]):
				
				minimum_available = node_data[1]
				which_node = key

		node = self.node_manager[which_node]

		host = node[0]

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

			sock_node.connect((host, 3114))

			while True:

				sock_node.sendall(package)
				reply = sock_node.recv(1024)
				node_size = manepack.desempacar_paquete_guardar_respuesta_ID_NM(reply, package[1])

				if node_size >= 0:

					self.page_manager[package[1]] = which_node
					node[1] = node_size
					break

			sock_node.close()

	# ------------------
	# Método que devuelve la respuesta al ML, cuuando el ML pide guardar
	# ------------------

	def save_data_answer(self, page_id):

		op_code = 2
		paquete = manepack.paquete_respuesta_guardar_ML_ID(op_code, page_id)
		return paquete

	# ------------------
	# Método que busca cual nodo tiene la página deseada y se la pide
	# ------------------

	def recover_data(self, package):

		for page in self.page_manager:

			if page == package[1]:

				node_number = self.page_manager[page]
				node_data = self.node_manager[node_number]
				host = node_data[0]

				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

					sock_node.connect((host, 3114))

					while True:

						sock_node.sendall(package)
						reply_package = sock_node.recv(8184)
		
						if reply_package[0] == 2:

							sock_node.close()
							return reply_package

		print ("Page does not exist in any node.")

class threadsDistributedInterface(threading.Thread):
    
	def __init__(self, name, interface):

		threading.Thread.__init__(self)
		self.name = name
		self.kill = False
		self.disInter = interface

	def run(self):

		my_name = self.name

		if(my_name == "sender"):

			interBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			interBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

			interBroad.bind(("", 44444))

			paquete = manepack.paquete_broadcast_quieroSer_ID_ID(0, self.disInter.mac_addres_in_bytes, self.disInter.round)

			while not self.kill:
				interBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
				print ("Mensaje quiero ser enviado, con ronda: " + str(self.disInter.round))
				time.sleep(4)

		elif(my_name == "receiver"):
			
			interClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			interClient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			interClient.bind(("", self.disInter.my_broadcast_port))

			# este while hay que cambiarlo a mientras la ronda sea >= 0
			while not self.kill:

				paquete, addr = interClient.recvfrom(1024)
				print ("Ip de la interfaz: " + str(addr[0]))

				datos = manepack.desempacar_paquete_quieroSer(paquete)

				if datos[1] == self.disInter.round:

					if datos[0] < self.disInter.raw_mac_address:

						self.disInter.round += 1

					else:

						self.disInter.round = -1

				elif datos[1] > self.disInter.round:

					self.disInter.round = -1

		elif(my_name == "nodeListener"):

			nodeBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			nodeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			nodeBroad.bind(("", 5000))

			while not self.kill:

				paquete, addr = nodeBroad.recvfrom(1024)
				print ("Ip del nodo de memoria: " + str(addr[0]))

				espacio_nodo = manepack.desempacar_paquete_estoyAqui(paquete)
				self.disInter.node_manager[self.disInter.nodeCounter] = [addr, espacio_nodo]
				self.disInter.nodeCounter += 1

		elif(my_name == "localMemoryListener"):

			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as memoryListener:

				memoryListener.bind((self.disInter.my_ip, 2000))
				memoryListener.listen()

				conn, addr = memoryListener.accept()
				
				with conn:

					while not self.kill:
						
						paquete = conn.recv(1024)

						if(paquete[0] == 0):

							self.disInter.save_data(paquete)
							answer_package = self.disInter.save_data_answer(paquete[1])
							conn.sendall(answer_package)

						elif(paquete[0] == 1):

							answer_package = self.disInter.recover_data(paquete)
							conn.sendall(answer_package)

# ------------------
# Método básico que revisa si los threads están vivos
# ------------------

def threads_alive(threads):

    if threads[0].is_alive() and threads[1].is_alive():

        return True

    else:

        return False

# ------------------
# Main de la interfaz
# ------------------

def main():

	threads = []
	distributedInterface = interfazDistribuida()

	threadSenderBC = threadsDistributedInterface(name = "sender", interface = distributedInterface)
	threadReceiverBC = threadsDistributedInterface(name = "receiver", interface = distributedInterface)
	threadMemoryNodeListener = threadsDistributedInterface(name = "nodeListener", interface = distributedInterface)
	threadLocalMemoryListener = threadsDistributedInterface(name = "localMemoryListener", interface = distributedInterface)

	threadSenderBC.start()
	threadReceiverBC.start()
	threadMemoryNodeListener.start()
	threadLocalMemoryListener.start()

	threads.append(threadSenderBC)
	threads.append(threadReceiverBC)
	threads.append(threadMemoryNodeListener)
	threads.append(threadLocalMemoryListener)

	while threads_alive(threads):

		try:

			[thread.join(1) for thread in threads
				if thread is not None and thread.is_alive()]

		except KeyboardInterrupt:

			print ("Killing threads")
			threadSenderBC.kill = True
			threadReceiverBC.kill = True

	print ("Everything compiles")

main()