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
		self.gloabal_ip = "127.0.0.1"
		self.my_broadcast_port = 6666
		self.my_tcp_port = 3114
		self.mac_addres_in_bytes = uuid.getnode().to_bytes(6, 'little')
		self.raw_mac_address = uuid.getnode()
		self.round = 0
		self.nodeCounter = 0
		self.pageCounter = 0
		self.sendChanges = False
		self.pasive = False
		self.startActive = False
		self.timeout_event = threading.Event()
		self.changedNodes = []
		self.changedPages = []

	# ------------------
	# Método que busca por best-fit cuál nodo es el más adecuado y guarda página
	# ------------------

	def save_data(self, package):

		minimum_available = 1000000000000
		which_node = -1

		for key in self.node_manager:

			node_data = self.node_manager[key]
			node_size = struct.unpack("I", package[2:6])

			if minimum_available > node_data[1] and node_data[1] >= node_size[0]:

				minimum_available = node_data[1]
				which_node = key

		if which_node == -1:

			print ("No hay espacio en ningun nodo")
			return 0

		node = self.node_manager[which_node]

		host = node[0]
		host_bytes = struct.pack("I", host)
		host_good_format = socket.inet_ntoa(host_bytes)

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

			sock_node.connect((host_good_format, 3114))

			while True:

				sock_node.sendall(package)
				reply = sock_node.recv(1024)
				node_size = manepack.desempacar_paquete_guardar_respuesta_ID_NM(reply, package[1])

				if node_size >= 0:

					self.page_manager[package[1]] = which_node
					self.changedPages.append(package[1])
					self.pageCounter += 1
					self.sendChanges = True
					node[1] = node_size
					break

			sock_node.close()
			return 1

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
						time.sleep(8)
						reply_package = sock_node.recv(691204)	# tamaño de la página más grande, más op code (1 byte) y id page (1 byte), más dos por si algo

						if reply_package[0] == 3:

							sock_node.close()
							return reply_package

		print ("Page does not exist in any node.")

	# ------------------
	# Método que crea el dump cuando la interfaz activa lo pida
	# El método piede devolver un dump completo de las tablas (para el primer broadcast de soy activo) o solo los cambios
	# Esos cambios se guardan en la lista changedPages y changedNodes
	# ------------------

	def create_dump(self, conCambio):

		dump1 = bytearray()
		dump2 = bytearray()

		for page in self.page_manager:

			if conCambio:

				for pageChanged in self.changedPages:

					if page == pageChanged:

						dump1.append(page)
						dump1.append(self.page_manager[page])

			else:

				dump1.append(page)
				dump1.append(self.page_manager[page])

		for node in self.node_manager:

			if conCambio:

				for numNode in self.changedNodes:

					if numNode == node:

						dump2.append(node)
						data = self.node_manager[node]

						ip_node = struct.pack("I", data[0])
						size_node = struct.pack("I", data[1])

						for i in range(4):

							dump2.append(ip_node[i])

						for i in range(4):

							dump2.append(size_node[i])

			else:

				dump2.append(node)
				data = self.node_manager[node]

				ip_node = struct.pack("I", data[0])
				size_node = struct.pack("I", data[1])

				for i in range(4):

					dump2.append(ip_node[i])

				for i in range(4):

					dump2.append(size_node[i])

		self.changedPages = []
		self.changedNodes = []
		return dump1, dump2

	# ------------------
	# Método que actualiza las tablas de la interfaz a partir del dump que recibió de la interfaz activa.
	# Solo actualiza los datos que no tiene
	# ------------------

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

			self.node_manager[node_dump[node_iterator]] = [ip[0], size[0]]
			node_iterator += 9
			node_amount -= 1

		self.nodeCounter = 0
		self.pageCounter = 0

		for key in self.node_manager:

			self.nodeCounter += 1

		for key in self.page_manager:

			self.pageCounter += 1

class threadsDistributedInterface(threading.Thread):

	def __init__(self, name, interface):

		threading.Thread.__init__(self)
		self.name = name
		self.kill = False
		self.disInter = interface

	def run(self):

		my_name = self.name

		# Thread quiero ser, el más importante. Este thread manda broadcast de quiero ser activo.
		# Cuando recibe broadcast pueden pasar tres cosas:
		#	* Que el timeout venca, si esto sucede y este thread sigue vivo, se proclama activo, entonces se adueña de la ip y cambia la variable active
		#	* Que reciba un paquete quiero ser, entonces ahi juegan la ronda comparando las direcciones MAC, el ganador sube su ronda y sigue escuchando, perdedor se hace pasivo
		#	* Que reciba un paquete soy activo o keep alive, en ese caso actualiza sus datos si tiene que, y pierde la champios y se declara pasivo

		if(my_name == "QuieroSerSender"):

			interBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			interBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			interBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			interBroad.setblocking(0)

			doBreak = False

			# broadcast dentro del lab
			interBroad.bind(("", self.disInter.my_broadcast_port))

			while not self.kill:

				if self.disInter.timeout_event.is_set():

					# Me apropio de la IP global para la interfaz

					print ("Me apropio de la IP: " + str(self.disInter.gloabal_ip))
					os.system('ifconfig eth0 down')
					os.system('ifconfig eth0 ' + str(self.disInter.gloabal_ip))
					os.system('ifconfig eth0 up')

					self.disInter.active = True
					break

				else:

					if not self.disInter.status:

						paquete = manepack.paquete_broadcast_quieroSer_ID_ID(0, self.disInter.mac_addres_in_bytes, self.disInter.round)
						interBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
						print ("Mensaje quiero ser enviado, con ronda: " + str(self.disInter.round))

						paquete_respuesta = []

						while not paquete_respuesta:

							try:
								#print ("intento recibir")
								paquete_respuesta, addr = interBroad.recvfrom(1024)

							except socket.error:

								pass

							if paquete_respuesta:

								if paquete_respuesta[0] == 0:

									datos = manepack.desempacar_paquete_quieroSer(paquete_respuesta)

									if datos[0] == self.disInter.raw_mac_address:

										paquete_respuesta = []

							if self.disInter.timeout_event.is_set():

								# Me apropio de la IP global para la interfaz

								print ("Me apropio de la IP: " + str(self.disInter.gloabal_ip))
								os.system('ifconfig eth0 down')
								os.system('ifconfig eth0 ' + str(self.disInter.gloabal_ip))
								os.system('ifconfig eth0 up')

								self.disInter.active = True
								break


						if paquete_respuesta:

							if paquete_respuesta[0] == 0:

								datos = manepack.desempacar_paquete_quieroSer(paquete_respuesta)

								# esta condicion debe ser diferente de, si está ogual a, entonces es para prueba
								if datos[0] != self.disInter.raw_mac_address:

									print ("Compito contra una interfaz con MAC: " + str(datos[0]))
									print ("Compito contra una interfaz con ronda: " + str(datos[1]))

									if datos[1] == self.disInter.round:

										if datos[0] < self.disInter.raw_mac_address:

											print ("Gane la ronda")
											self.disInter.round += 1

										else:

											self.disInter.round = 3
											self.disInter.status = True
											print ("He perdido la champions, me delcaro interfaz pasiva")
											doBreak = True
											break

									elif datos[1] > self.disInter.round:

										self.disInter.round = 3
										self.disInter.status = True
										print ("Estoy atrasado en la champions, así que me declaro pasiva")
										doBreak = True
										break

							elif paquete_respuesta[0] == 1:

								print ("Ya hay interfaz activa. Me declaro pasiva.")
								datos = manepack.desempacar_paquete_soyActivo(paquete_respuesta)
								print ("Dump recibido: " + str(datos))

								self.disInter.update_with_dump(datos)
								self.disInter.round = 3
								self.disInter.status = True
								doBreak = True
								break

							elif paquete_respuesta[0] == 2:

								print ("Ya hay interfaz activa. Me declaro pasiva.")
								datos = manepack.desempacar_paquete_keepAlive(paquete_respuesta)

								if datos != 0:

									print ("Dump recibido: " + str(datos))
									self.disInter.update_with_dump(datos)
									self.disInter.round = 3
									self.disInter.status = True
									doBreak = True
									break

								break

						else:

							break

					if doBreak:
						break

				#time.sleep(4)

			self.disInter.status = True
			self.disInter.startChampions = False
			interBroad.close()

		# Thread para el timeout de la champions, el timeout debe ser 3 segundos, si hay otro es para prueba
		# Cuando el timeout se vence envía un evento, el cual es explicado en el thread de quiero ser

		elif(my_name == "timeout"):

			time.sleep(5)
			self.disInter.timeout_event.set()

		# Thread activo, este thread inicialmente cuando se activa manda el mensaje soy activo y hace un dump de sus tablas
		# Luego comienza a enviar keep alives, y si recibe que hubo cambios en las tablas, manda keep alive con cambios

		elif(my_name == "soyActivo"):

			activeBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			activeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			activeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

			activeBroad.bind(("", 44444))

			dump1, dump2 = self.disInter.create_dump(0)
			paquete = manepack.paquete_broadcast_soyActivo_ID_ID(1, self.disInter.pageCounter, self.disInter.nodeCounter, dump1, dump2)
			activeBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))

			print("Paquete soy activo enviado")
			time.sleep(2)

			while not self.kill:

				if self.disInter.sendChanges:

					self.disInter.sendChanges = False

					row1 = len(self.disInter.changedPages)
					row2 = len(self.disInter.changedNodes)
					dump1, dump2 = self.disInter.create_dump(1)
					paquete = manepack.paquete_broadcast_keepAlive_ID_ID(2, row1, row2, dump1, dump2)

					activeBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
					print ("Paquete keep alive con cambios enviado")

				else:

					paquete = manepack.paquete_broadcast_keepAlive_ID_ID(2, 0, 0, 0, 0)
					activeBroad.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))
					print ("Paquete keep alive sin cambios enviado")

				time.sleep(2)

			activeBroad.close()

		# Thread que escucha broadcast en el peurto de las interfaces (6666)
		# Este thread se activa junto al activo, con el fin de responderle a las interfaces que lleguen después reportándose con un quiero ser
		# Este thread tiene el objetivo de mandarle el dump, muere junto con el acitvo

		elif(my_name == "activoListener"):

			print ("Thread activo listener iniciado")

			activeBroadListen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			activeBroadListen.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			activeBroadListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

			activeBroadListen.bind(("", self.disInter.my_broadcast_port))

			while not self.kill:

				paquete, addr = activeBroadListen.recvfrom(1024)

				if paquete[0] == 0:

					datos = manepack.desempacar_paquete_quieroSer(paquete)

					if datos[0] != self.disInter.mac_addres_in_bytes:

						print ("Se envía dump a " + str(addr) + " que acaba de levantarse mientras yo soy activo")

						dump1, dump2 = self.disInter.create_dump(0)
						paquete = manepack.paquete_broadcast_soyActivo_ID_ID(1, self.disInter.pageCounter, self.disInter.nodeCounter, dump1, dump2)
						activeBroadListen.sendto(paquete, ('<broadcast>', self.disInter.my_broadcast_port))

			activeBroadListen.close()

		# Thread que escucha los broadcast de los nodos de memoria, guarda el nodo con su respectivo espacio
		# Además pone la variable send changes en True, con el fin de que el thread activo mande un keep alive con cambios

		elif(my_name == "nodeListener"):

			nodeBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			nodeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			nodeBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			nodeBroad.bind(("", 5000))

			while not self.kill:

				repetido = False

				paquete, addr = nodeBroad.recvfrom(1024)
				print ("Ip del nodo de memoria: " + str(addr[0]))

				ip_nodo_byte = socket.inet_aton(addr[0])
				ip_nodo = struct.unpack("I", ip_nodo_byte)
				espacio_nodo = manepack.desempacar_paquete_estoyAqui(paquete)

				for key in self.disInter.node_manager:

					node_data = self.disInter.node_manager[key]

					if node_data[0] == ip_nodo[0]:
						repetido = True

				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

					sock_node.connect((addr[0], 3114))
					answer = 2
					answer = answer.to_bytes(1, 'big')
					sock_node.sendall(answer)
					sock_node.close()

				if not repetido:

					self.disInter.node_manager[self.disInter.nodeCounter] = [ip_nodo[0], espacio_nodo]
					self.disInter.changedNodes.append(self.disInter.nodeCounter)
					self.disInter.nodeCounter += 1
					self.disInter.sendChanges = True

			nodeBroad.close()

		# Thread que escucha a la memoria local, sus request de guardar y pedir página

		elif(my_name == "localMemoryListener"):

			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as memoryListener:

				memoryListener.bind(('192.168.50.51', 2000))

				memoryListener.listen()
				conn, addr = memoryListener.accept()

				while not self.kill:

					#with conn
					paquete = conn.recv(691208)

					if(paquete[0] == 0):

						saved = self.disInter.save_data(paquete)

						if saved:

							page_size = struct.unpack("I", paquete[2:6])
							print ("Se guardó página con ID: " + str(paquete[1]) + " y tamaño: " + str(page_size[0]))
							answer_package = self.disInter.save_data_answer(paquete[1])
							conn.sendall(answer_package)

						else:

							answer_package = manepack.paquete_respuesta_guardar_ML_ID(4, paquete[1])
							conn.sendall(answer_package)

					elif(paquete[0] == 1):

						answer_package = self.disInter.recover_data(paquete)
						conn.sendall(answer_package)


				memoryListener.close()


		# Thread que maneja la interfaz pasiva, siempre va estar escuchando broadcast por parte del activo
		# Si el paquete keep alive trae datos, actualiza las tablas de la interfaz
		# Si se vence el timeout de dos segundos, entonces indica que la activa no responde y va iniciar otra champions

		elif(my_name == "soyPasivo"):

			pasiveBroad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			pasiveBroad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			pasiveBroad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			pasiveBroad.bind(("", self.disInter.my_broadcast_port))
			#pasiveBroad.settimeout(3)

			while not self.kill:

				timeout = select.select([pasiveBroad], [], [], 5)

				if timeout[0]:

					paquete, addr = pasiveBroad.recvfrom(65536)

					if paquete[0] == 1:

						datos = manepack.desempacar_paquete_soyActivo(paquete)
						self.disInter.update_with_dump(datos)

					elif paquete[0] == 2:

						datos = manepack.desempacar_paquete_keepAlive(paquete)

						if datos != 0:

							self.disInter.update_with_dump(datos)

				else:

					print ("Interfaz activa no responde")
					self.disInter.status = False
					self.disInter.startChampions = True
					break

			self.disInter.pasive = False
			pasiveBroad.close()

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

	threads = []
	distributedInterface = interfazDistribuida()

	while 1:

		try:

			[thread.join(1) for thread in threads
				if thread is not None and thread.is_alive()]

			# Si ya se hizo champions, y active está en true y no hay una activa, entonces significa que mi interfaz quedó como activa
			# Entonces inicia el thread de la interfaz activa, además el thread que escucha a memoria local y el que escucha broadcast de nodos de memoria

			if distributedInterface.status == True and distributedInterface.active == True and not distributedInterface.startActive:

				print ("Thread activo activado")
				distributedInterface.startActive = True

				threadMemoryNodeListener = threadsDistributedInterface(name = "nodeListener", interface = distributedInterface)
				threadLocalMemoryListener = threadsDistributedInterface(name = "localMemoryListener", interface = distributedInterface)
				threadSoyActivo = threadsDistributedInterface(name = "soyActivo", interface = distributedInterface)
				threadSoyActivoListener = threadsDistributedInterface(name = "activoListener", interface = distributedInterface)

				threadMemoryNodeListener.start()
				threadLocalMemoryListener.start()
				threadSoyActivo.start()
				threadSoyActivoListener.start()

				threads.append(threadMemoryNodeListener)
				threads.append(threadLocalMemoryListener)
				threads.append(threadSoyActivo)
				threads.append(threadSoyActivoListener)

			# Si ya se hizo la champions, active está en false y no hay una pasiva, entonces significa que mi interfaz quedó como activa

			elif distributedInterface.status == True and distributedInterface.active == False and not distributedInterface.pasive:

				print ("Thread pasivo activado")
				distributedInterface.pasive = True

				threadSoyPasivo = threadsDistributedInterface(name = "soyPasivo", interface = distributedInterface)
				threadSoyPasivo.start()
				threads.append(threadSoyPasivo)

			# Si no se ha hecho champions, y la variable de empezar champions está en true entonces la inicio
			# Inicio el thread que envía los mensajes quiero ser, además inicia el thread que controla el timeout para mi interfaz

			elif distributedInterface.status == False and distributedInterface.startChampions == True:

				print ("Inicia champions")
				distributedInterface.timeout_event.clear()

				threadSenderBC = threadsDistributedInterface(name = "QuieroSerSender", interface = distributedInterface)
				threadTimeout = threadsDistributedInterface(name = "timeout", interface = distributedInterface)

				threadSenderBC.start()
				threadTimeout.start()

				threads.append(threadSenderBC)
				threads.append(threadTimeout)

				distributedInterface.startChampions = False

		# Si se da este except, entonces mata los threads, a veces necesita que se haga Control + C dos veces

		except KeyboardInterrupt:

			print ("Killing threads")

			for thread in threads:

				thread.kill = True

			break

	print ("Main thread exited")

main()
