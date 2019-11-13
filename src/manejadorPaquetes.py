import struct

# ------------------------
# Método para ML o ID para crear el paquete que indica que quiere guardar datos
# Este es el paquete que se le envía al ID o al NM cuando se quiere guardar página
# ------------------------

def paquete_para_guardar(op_code, id_page, page_size, data):

    package_format = "=BBI" + str(page_size) + "s"
    package = struct.pack(package_format, op_code, id_page, page_size, data)

    return package

# ------------------------
# Método para ML o ID para crear el paquete que indica que quiere leer datos
# Este es el paque se le envía al ID o al NM cuando se quiere leer página
# ------------------------

def paquete_para_leer(op_code, id_page):

    package_format = "=BB"
    package = struct.pack(package_format, op_code, id_page)

    return package

# ------------------------
# Método para ID para dar respuesta a un request de guardar del ML
# Este es el paquete que se le devuelve al ML cuando pide guardar
# ------------------------

def paquete_respuesta_guardar_ML_ID(op_code, id_page):

    package_format = "=BB"
    package = struct.pack(package_format, op_code, id_page)

    return package

# ------------------------
# Método para NM para dar respuesta a un request de guardar del ID
# Este es el paquete que se le devuelve al ID cuando pide guardar
# ------------------------

def paquete_respuesta_guardar_ID_NM(op_code, id_page, node_size):

    package_format = "=BBI"
    package = struct.pack(package_format, op_code, id_page, node_size)

    return package

# ------------------------
# Método para ID o NM cuando recibe request de lectura
# Este es el paquete que se le devuelve al ML o al ID depende de quien quiere página
# ------------------------

def paquete_respuesta_leer(op_code, id_page, data):

    package_format = "=BB" + str(len(data)) + "s"
    package = struct.pack(package_format, op_code, id_page, data)

    return package

# ------------------------
# Método para ML cuando recibe la respuesta al request de guardar que realizó
# Retorna 0 cuando se guarda exitosamente, 1 cuando hubo problema
# ------------------------

def desempacar_paquete_guardar_respuesta_ML_ID(paquete, id_page):

    op_code_res = paquete[0]
    id_page_res = paquete[1]

    if op_code_res == 3:

        print ("Se produjo error al guardar la página")
        return 1

    else:

        if id_page_res == id_page:

            print ("Se guardó exitosamente")
            return 0

        else:

            print ("Se guardó página incorrecta")
            return 1

# ------------------------
# Método para ID cuando recibe la respuesta al request de guardar que realizó
# Retorna el tamaño restante del nodo de memoria
# ------------------------

def desempacar_paquete_guardar_respuesta_ID_NM(paquete, id_page):

    op_code_res = paquete[0]
    id_page_res = paquete[1]
    node_size = struct.unpack("I", paquete[2:6])

    if op_code_res == 3:

        print ("Se produjo error al guardar página")
        return 1

    else:

        if id_page_res == id_page:

            print ("Se guardó exitosamente")
            print ("Espacio disponible en el nodo: " + str(node_size[0]) + " bytes")
            return node_size[0]

        else:

            print ("Se guardó página incorrecta")
            return 1


# ------------------------
# Método para ML O ID cuando recibe la respuesta al request de leer que realizó
# Retorna los datos de la página que pidió
# ------------------------

def desempacar_paquete_respuesta_leer(paquete, page_id, page_size):

    op_code_res = paquete[0]
    id_page_res = paquete[1]
    data = paquete[2:(2+page_size)]

    if op_code_res == 3:

        print ("Se produjo error al devolver página")
        return 1

    else:

        if id_page_res == page_id:

            print ("Se obtuvo la página exitosamente")
            return data