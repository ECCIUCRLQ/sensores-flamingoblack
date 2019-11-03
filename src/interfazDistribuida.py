# coding=utf-8
import time
import os


class interface:

	def __init__(self):

		# Hash que mantiene los metadatos de los nodos
		self.node_manager = {

			# la hash crece conforme llegan mas nodos
			# identificador: [ip, lista con paginas en ese nodo, espacio disponible en el nodo]

			1: [-1, [], -1],
			2: [-1, [], -1],
			3: [-1, [], -1],
			4: [-1, [], -1]
		}

		# Hash que crecera a medida que lleguen paginas, se asocia pagina:nodo
		self.page_manager = {

		}

		self.active = False
		self.myIp = "127.0.0.1"

	# ------------------
	# Método que buscar por best-fit cuál nodo es el más adecuado
	# ------------------

	def save_data(self, data_to_be_saved):
		
		minimum_available = 100000000
		which_node = 0
		
		for key in self.node_manager:
			
			node_data = self.node_manager[key]
			
			if minimum_available > node_data[2] and node_data[2] > len(data_to_be_saved):
				
				minimum_available = node_data[2]
				which_node = key
				
		# se manda al nodo which_node el dato
		# se espera de vuelta el tamaño con el que quedo para actualizar
	

	# ------------------
	# Método que itera sobre la lista de páginas y le pide a los nodos los datos, duerme 5 segundos por cada envio al administrador local
	# ------------------

	def recover_data(self, page_list):
		
		for page in page_list:
			
			for page_node in self.page_manager:
				
				if page_node == page:
					
					# le pido al nodo que me envie esa pagina
					# le envio esa pagina a la memoria local
					time.sleep(5)

		return 0

	def set_active_interface(self, ipList):

		lowestIp = ""

		for ip in ipList:

			if lowestIp < ipList[ip]:

				lowestIp = ipList[ip]

		if lowestIp == self.myIp:

			self.active = True
			# hago broadcast que soy activo

		return 0

print ("Todo compila")