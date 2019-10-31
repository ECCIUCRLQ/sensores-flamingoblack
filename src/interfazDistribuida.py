import time
import os

# ------------------
# Hash que mantiene los metadatos de los nodos
# ------------------

node_manager = {

	# la hash crece conforme llegan mas nodos
	# identificador: [ip, lista con paginas en ese nodo, espacio disponible en el nodo]

	1: [-1, [], -1]
	2: [-1, [], -1]
	3: [-1, [], -1]
	4: [-1, [], -1]
}

# ------------------
# Hash que crecera a medida que lleguen paginas, se asocia pagina:nodo
# ------------------

page_ manager {

}

def save_data(data_to_be_saved):
	
	minimum_available = 100000000
	which_node = 0
	
	for key in node_manager:
		
		node_data = node_manager[key]
		
		if minimum_available > node_data[2] and node_data[2] > len(data_to_be_saved):
			
			minimum_available = node_data[2]
			which_node = key
			
	# se manda al nodo which_node el dato
	# se espera de vuelta el tamaño con el que quedo para actualizar
	
def recover_data(page_list):
	
	for page in page_list:
		
		for page_node in page_manager:
			
			if page_node == page:
				
				# le pido al nodo que me envie esa pagina
				# le envio esa pagina a la memoria local
				time.sleep(5)
