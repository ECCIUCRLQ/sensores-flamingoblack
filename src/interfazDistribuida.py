# coding=utf-8
import time
import os
import socket
import struct
import uuid
import threading
import select
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
		self.startChampions = True
		self.my_ip = "127.0.0.1"
		self.my_broadcast_port = 6666
		self.my_tcp_port = 3114
		self.mac_addres_in_bytes = uuid.getnode().to_bytes(6, 'little')
		self.raw_mac_address = uuid.getnode()
		self.round = 0
		self.nodeCounter = 0
		self.pageCounter = 0
		self.sendChanges = False
		self.pasive = False

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
					self.pageCounter += 1
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

				ip = node_data[0]
				ip_bytes = struct.pack("I", ip)
				host = socket.inet_ntoa(ip_bytes)

				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

					sock_node.connect((host, 3114))

					while True:

						sock_node.sendall(package)
						reply_package = sock_node.recv(691204)	# tamaño de la página más grande, más op code (1 byte) y id page (1 byte), más dos por si algo
		
						if reply_package[0] == 2:

							sock_node.close()
							return reply_package

		print ("Page does not exist in any node.")

	def create_dump(self):

		dump1 = bytearray()
		dump2 = bytearray()

		for page in self.page_manager:

			dump1.append(page)
			dump1.append(self.page_manager[page])

		for node in self.node_manager:

			dump2.append(node)
			data = self.node_manager[node]
			
			ip_node = struct.pack("I", data[0])
			size_node = struct.pack("I", data[1])

			for i in range(4):

				dump2.append(ip_node[i])
			
			for i in range(4):

				dump2.append(size_node[i])

		return dump1, dump2

	def update_with_dump(self, data):

		page_amount = data[0]
		page_dump = data[2]

		page_iterator = 0

		while page_amount > 0:

			self.page_manager[page_dump[page_iterator]] = page_dump[page_iterator+1]
			page_iterator += 2
			page_amount -= 1

		node_amount = data[1]
		node_dump = data[3]

		node_iterator = 0

		while node_amount > 0:

			ip = struct.unpack("I", node_dump[node_iterator+1:(node_iterator+1)+4])
			size = struct.unpack("I", node_dump[(node_iterator+1)+4:((node_iterator+1)+4)+4])

			value = [ip, size]
			self.node_manager[node_dump[node_iterator]] = value
			node_iterator += 9
			node_amount -= 1

class threadsDistributedInterface(threading.Thread):
    
	def __init__(self, name, interface):

		threading.Thread.__init__(self)
		self.name = name
		self.kill = False
		self.disInter = interface

	def run(self):

		my_name = self.name

		if(my_name == "QuieroSerSender"):

			interBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			interBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

			interBroad.bind(("", 44444))

			while not self.kill:

				if self.disInter.status == True:

					break

				else:

					paquete = manepack.paquete_broadcast_quieroSer_ID_ID(0, self.disInter.mac_addres_in_bytes, self.disInter.round)
					interBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
					print ("Mensaje quiero ser enviado, con ronda: " + str(self.disInter.round))

				time.sleep(4)

			interBroad.close()

		elif(my_name == "QuieroSerReceiver"):
			
			interClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			interClient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			interClient.bind(("", self.disInter.my_broadcast_port))

			while not self.kill:

				paquete, addr = interClient.recvfrom(1024)
				#print ("Ip de la interfaz: " + str(addr[0]))

				datos = manepack.desempacar_paquete_quieroSer(paquete)

				# esta condicion debe ser diferente de, está igual a para prueba
				if datos[0] == self.disInter.raw_mac_address:

					if datos[1] == self.disInter.round:

						if datos[0] < self.disInter.raw_mac_address:

							self.disInter.round += 1

						else:

							self.disInter.round = 10
							print ("He perdido la champions, me delcaro interfaz activa")
							break

					elif datos[1] > self.disInter.round:

						self.disInter.round = 10
						print ("Estoy atrasado en la champions, así que me declaro activo")
						break

			self.disInter.status = True
			self.disInter.startChampions = False
			interClient.close()

		elif(my_name == "soyActivo"):

			activeBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			activeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

			activeBroad.bind(("", 44444))

			dump1, dump2 = self.disInter.create_dump()
			paquete = manepack.paquete_broadcast_soyActivo_ID_ID(1, self.disInter.pageCounter, self.disInter.nodeCounter, dump1, dump2)
			activeBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))

			while not self.kill:

				if self.disInter.sendChanges:

					self.disInter.sendChanges = False
					dump1, dump2 = self.disInter.create_dump()
					paquete = manepack.paquete_broadcast_keepAlive_ID_ID(2, self.disInter.pageCounter, self.disInter.nodeCounter, dump1, dump2)
					activeBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
					print ("Paquete keep alive con cambios enviado")

				else:

					paquete = manepack.paquete_broadcast_keepAlive_ID_ID(2, 0, 0, 0, 0)
					activeBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
					print ("Paquete keep alive sin cambios enviado")
				
				time.sleep(4)

		elif(my_name == "soyPasivo"):

			pasiveBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			pasiveBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			pasiveBroad.bind(("", self.disInter.my_broadcast_port))
			pasiveBroad.settimeout(4) # todavía no sé bien el timeout

			timeout = select.select([pasiveBroad], [], [], 4)

			while not self.kill:

				if timeout[0]:

					paquete, addr = pasiveBroad.recvfrom(65536)

					if paquete[0] == 1 or paquete[0] == 2:
					
						datos = manepack.desempacar_paquete_keepAlive(paquete)

						if datos > 1:

							self.disInter.update_with_dump(datos)

				else:

					print ("Interfaz activa no responde")
					self.disInter.status = False
					self.disInter.startChampions = True
					break

			self.disInter.pasive = False
			pasiveBroad.close()

		elif(my_name == "nodeListener"):

			nodeBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			nodeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			nodeBroad.bind(("", 5000))

			while not self.kill:

				paquete, addr = nodeBroad.recvfrom(1024)
				print ("Ip del nodo de memoria: " + str(addr[0]))

				ip_nodo_byte = socket.inet_aton(addr)
				ip_nodo = struct.unpack("I", ip_nodo_byte)
				espacio_nodo = manepack.desempacar_paquete_estoyAqui(paquete)
				
				self.disInter.node_manager[self.disInter.nodeCounter] = [ip_nodo[0], espacio_nodo]
				self.disInter.nodeCounter += 1
				self.disInter.sendChanges = True

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
							self.disInter.sendChanges = True
							answer_package = self.disInter.save_data_answer(paquete[1])
							conn.sendall(answer_package)

						elif(paquete[0] == 1):

							answer_package = self.disInter.recover_data(paquete)
							conn.sendall(answer_package)

# ------------------
# Método básico que revisa si los threads están vivos
# ------------------

def threads_alive(threads):

	for thread in threads:

		if not thread.is_alive():

			return False

	return True

# ------------------
# Main de la interfaz
# ------------------

def main():

	#threads = []
	distributedInterface = interfazDistribuida()

	#threadSenderBC = threadsDistributedInterface(name = "QuieroSerSender", interface = distributedInterface)
	#threadReceiverBC = threadsDistributedInterface(name = "QuieroSerReceiver", interface = distributedInterface)
	#threadMemoryNodeListener = threadsDistributedInterface(name = "nodeListener", interface = distributedInterface)
	#threadLocalMemoryListener = threadsDistributedInterface(name = "localMemoryListener", interface = distributedInterface)
	#threadSoyActivo = threadsDistributedInterface(name = "soyActivo", interface = distributedInterface)
	#threadSoyPasivo = threadsDistributedInterface(name = "soyPasivo", interface = distributedInterface)

	while 1:

		try:

			#[thread.join(1) for thread in threads
			#	if thread is not None and thread.is_alive()]

			if distributedInterface.status == True and distributedInterface.active == True:

				print ("Thread activo activado")
				
				threadMemoryNodeListener = threadsDistributedInterface(name = "nodeListener", interface = distributedInterface)
				threadLocalMemoryListener = threadsDistributedInterface(name = "localMemoryListener", interface = distributedInterface)
				threadSoyActivo = threadsDistributedInterface(name = "soyActivo", interface = distributedInterface)

				threadMemoryNodeListener.start()
				threadLocalMemoryListener.start()
				threadSoyActivo.start()

				#threads.append(threadMemoryNodeListener)
				#threads.append(threadLocalMemoryListener)
				#threads.append(threadSoyActivo)

			elif distributedInterface.status == True and distributedInterface.active == False and not distributedInterface.pasive:

				print ("Thread pasivo activado")
				distributedInterface.pasive = True

				threadSoyPasivo = threadsDistributedInterface(name = "soyPasivo", interface = distributedInterface)
				threadSoyPasivo.start()
				#threads.append(threadSoyPasivo)

			elif distributedInterface.status == False and distributedInterface.startChampions == True:

				print ("Inicia champions")
				time.sleep(5)

				threadSenderBC = threadsDistributedInterface(name = "QuieroSerSender", interface = distributedInterface)
				threadReceiverBC = threadsDistributedInterface(name = "QuieroSerReceiver", interface = distributedInterface)

				threadSenderBC.start()
				threadReceiverBC.start()

				#threads.append(threadSenderBC)
				#threads.append(threadReceiverBC)

				distributedInterface.startChampions = False

		except KeyboardInterrupt:

			print ("Killing threads")
			threadSenderBC.kill = True
			threadReceiverBC.kill = True
			threadLocalMemoryListener.kill = True
			threadMemoryNodeListener.kill = True
			threadSoyActivo.kill = True
			threadSoyPasivo.kill = True

	print ("Main thread exited")

main()