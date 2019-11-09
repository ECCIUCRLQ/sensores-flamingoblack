# coding=utf-8
import time
import os
import socket
import struct

class interface:

	def __init__(self):

		# Hash que mantiene los metadatos de los nodos
		self.node_manager = {

			# la hash crece conforme llegan mas nodos
			# identificador: [ip, puerto, lista con paginas en ese nodo, espacio disponible en el nodo]

			1: [-1, -1, [], -1],
			2: [-1, -1, [], -1],
			3: [-1, -1, [], -1],
			4: [-1, -1, [], -1]
		}

		# Hash que crecera a medida que lleguen paginas, se asocia pagina:nodo
		self.page_manager = {

		}

		self.active = False
		self.myIp = "127.0.0.1"
		self.myPort = 5015

	# ------------------
	# Método que construye el paquete que le va a mandar al nodo de memoria cuando quiera guardar
	# ------------------

	def node_package_sender(self, page_id, page_size, data_to_be_saved):

		op_code = 0x00
		package = [op_code, page_id, page_size, data_to_be_saved]
		return package

	# ------------------
	# Método que construye el paquete que le va a mandar al nodo de memoria cuando quiere recuperar página
	# ------------------

	def node_package_receiver(self, page_id):

		op_code = 0x01
		package = [op_code, page_id]
		return package

	# ------------------
	# Método que busca por best-fit cuál nodo es el más adecuado y guarda página
	# ------------------

	def save_data(self, page_id, page_size, data_to_be_saved):
		
		package = self.node_package_sender(page_id, page_size, data_to_be_saved)
		raw_package = bytes(package)

		minimum_available = 100000000
		which_node = 0
		
		for key in self.node_manager:
			
			node_data = self.node_manager[key]
			
			if minimum_available > node_data[2] and node_data[2] > len(data_to_be_saved):
				
				minimum_available = node_data[2]
				which_node = key

		node = self.node_manager[which_node]

		host = node[0]
		port = node[1]

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

			sock_node.connect((host, port))

			while True:

				sock_node.sendall(raw_package)
				reply = sock_node.recv(1024)
		
				if reply[0] == 1:

					self.page_manager[page_id] = which_node

					node[2].append(page_id)
					node[3] = reply[1]
					break

			sock_node.close()

	# ------------------
	# Método que busca cual nodo tiene la página deseada y se la pide
	# ------------------

	def recover_data(self, page_id, page_size):

		for page in self.page_manager:

			if page == page_id:

				node = self.page_manager[page]
				host = node[0]
				port = node[1]

				package = self.node_package_receiver(page_id)
				raw_package = bytes(package)

				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_node:

					sock_node.connect((host, port))

					while True:

						sock_node.sendall(raw_package)
						reply = sock_node.recv((page_size+1))
		
						if reply[0] == 1:

							sock_node.close()
							return reply[1]

			else:

				print ("Page does not exist in any node.")

	'''

	# ------------------
	# Método que establece la interfaz activa
	# ------------------

	def set_active_interface(self):

		lowestIp = self.myIp
		host = ''
		port = self.myPort

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockServer:
    		
			sockServer.bind((host, port))
    		sockServer.listen(1)
    		conn, addr = sockServer.accept()
    		
			with conn:
        
				print("Interfaz con ip: " + addr + " se ha reportado.")
				while True:
            
					data = conn.recv(1024)
					if not data: break
        
						conn.sendall(data)

		for ip in ipList:

			if lowestIp < ipList[ip]:

				lowestIp = ipList[ip]

		if lowestIp == self.myIp:

			self.active = True
			# hago broadcast que soy activo

		return 0

	def broadcast_to_all_interface(self):

		host = ''
		port = 10000

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as broadcastSock:
    
			broadcastSock.connect((HOST, PORT))
    		broadcastSock.sendall(b'Cliente 1')
    		data = broadcastSock.recv(1024)

		print('Received', repr(data))

	'''

print ("Todo compila")