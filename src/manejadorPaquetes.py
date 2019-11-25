# coding=utf-8
import struct

# ------------------------
# Método para ML o ID para crear el paquete que indica que quiere guardar datos
# Este es el paquete que se le envía al ID o al NM cuando se quiere guardar página
# ------------------------

def paquete_para_guardar(op_code, id_page, page_size, data):

    package_format = "=BBI"
    package = struct.pack(package_format, op_code, id_page, page_size)

    package += data
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

    package_format = "=BB"
    package = struct.pack(package_format, op_code, id_page)

    package += data
    return package

# ------------------------
# Método para ID cuando quiere mandar broadcast de quiero ser activo
# Este es el paquete que se manda por el broadcast hacia las interfaces
# Estructura [op_code (1 byte), mac (6 bytes), round (1 byte)]
# ------------------------

def paquete_broadcast_quieroSer_ID_ID(op_code, mac_address, round_num):

    package_format = "=B6sB"
    package = struct.pack(package_format, op_code, mac_address, round_num)

    return package

# ------------------------
# Método para ID cuando quiere mandar broadcast de soy activo
# Este es el paquete que se manda por el broadcast hacia las interfaces
# Estructura [op_code (1 byte), filas1 (1 byte), filas2 (1 byte), dump1 (filas1 * 2 bytes), dump2 (filas2 * 9 bytes)]
# ------------------------

def paquete_broadcast_soyActivo_ID_ID(op_code, row1, row2, dump1, dump2):

    package_format = "=BBB"
    package = struct.pack(package_format, op_code, row1, row2)

    package += dump1
    package += dump2
    return package

# ------------------------
# Método para ID cuando quiere mandar broadcast de keep alive
# Este es el paquete que se manda por el broadcast hacia las interfaces
# Estructura [op_code (1 byte), filas1 (1 byte), filas2 (1 byte), dump1 (filas1 * 2 bytes), dump2 (filas2 * 9 bytes)]
# Si los parámetros de fila1 y fila2 vienen en cero, significa que es un keep alive normal
# ------------------------

def paquete_broadcast_keepAlive_ID_ID(op_code, row1, row2, dump1, dump2):

    if row1 or row2 > 0:

        package_format = "=BBB"
        package = struct.pack(package_format, op_code, row1, row2)

        package += dump1
        package += dump2
        return package

    else:

        package_format = "=BBBBB"
        package = struct.pack(package_format, op_code, row1, row2, dump1, dump2)

        return package

# ------------------------
# Método para NM cuando quiere mandar broadcast de me acaban de levantar
# Este es el paquete que se manda por el broadcast hacia las interfaces
# Estructura [op_code (1 byte), node_size (4 bytes)]
# ------------------------

def paquete_broadcast_estoyAqui_NM_ID(op_code, node_size):

    package_format = "=BI"
    package = struct.pack(package_format, op_code, node_size)

    return package

# ------------------------
# Método para ML cuando recibe la respuesta al request de guardar que realizó
# Retorna 0 cuando se guarda exitosamente, 1 cuando hubo problema
# ------------------------

def desempacar_paquete_guardar_respuesta_ML_ID(paquete, id_page):

    op_code_res = paquete[0]
    id_page_res = paquete[1]

    if op_code_res == 4:

        print ("Se produjo error al obtener la página en ID")
        return 1

    else:

        if id_page_res == id_page:

            print ("ID obtuvo página exitosamente")
            return 0

        else:

            print ("ID obtuvo página incorrecta")
            return 1

# ------------------------
# Método para ID cuando recibe la respuesta al request de guardar que realizó
# Retorna el tamaño restante del nodo de memoria
# ------------------------

def desempacar_paquete_guardar_respuesta_ID_NM(paquete, id_page):

    op_code_res = paquete[0]
    id_page_res = paquete[1]
    node_size = struct.unpack("I", paquete[2:6])

    if op_code_res == 4:

        print ("Se produjo error al guardar página en NM")
        return -1

    else:

        if id_page_res == id_page:

            print ("Se guardó exitosamente en NM")
            print ("Espacio disponible en el nodo: " + str(node_size[0]) + " bytes")
            return node_size[0]

        else:

            print ("Se guardó página incorrecta en NM")
            return -1


# ------------------------
# Método para ML O ID cuando recibe la respuesta al request de leer que realizó
# Retorna los datos de la página que pidió
# ------------------------

def desempacar_paquete_respuesta_leer(paquete, page_id, page_size):

    op_code_res = paquete[0]
    id_page_res = paquete[1]
    data = paquete[2:(2+page_size)]

    if op_code_res == 4:

        print ("Se produjo error al devolver página")
        return 1

    else:

        if id_page_res == page_id:

            print ("Se obtuvo la página exitosamente")
            return data

        else:

            print ("ID obtuvo página incorrecta")
            return 1

# ------------------------
# Método para ID cuando recibe un paquete quiero ser activo
# Retorna la direccion MAC y la ronda, respectivamente
# ------------------------

def desempacar_paquete_quieroSer(paquete):

    op_code, mac1, mac2, ronda = struct.unpack('=BHIB', paquete)

    if op_code == 4:

        print ("Se produjo error en una interfaz que quiere ser interfaz activa")
        return 1

    else:

        mac = mac1 | (mac2 << 16)
        print ("Una interfaz se ha reportado con su MAC: " + str(mac))
        print ("Una interfaz se ha reportado con ronda: " + str(ronda))
        return [mac, ronda]

# ------------------------
# Método para ID cuando recibe un paquete soy activo
# Retorna la cantidad de fila para las tablas, y sus respectivos datos
# ------------------------

def desempacar_paquete_soyActivo(paquete):

    op_code_res = paquete[0]

    if op_code_res == 4:

        print ("Se produjo error al iniciarse como activo")
        return 0

    else:

        filas_tabla1 = paquete[1]
        filas_tabla2 = paquete[2]

        tamano_datos1 = filas_tabla1 * 2
        datos_tabla1 = paquete[3:(3+tamano_datos1)]

        tamano_datos2 = filas_tabla2 * 9
        datos_tabla2 = paquete[(3+tamano_datos1):(3+tamano_datos1+tamano_datos2)]

        return [filas_tabla1, filas_tabla2, datos_tabla1, datos_tabla2]

# ------------------------
# Método para ID cuando recibe un paquete keep alive
# Retorna la direccion MAC y la ronda, respectivamente, esto solo si el tamaño de fila1 y filas2 es mayor a cero
# Si el tamaño de las filas es 0, significa que es un keep alive normal
# ------------------------

def desempacar_paquete_keepAlive(paquete):

    op_code_res = paquete[0]

    if op_code_res == 4:

        print ("Se produjo error al enviar Keep Alive")
        return 1

    else:

        if paquete[1] and paquete[2] > 0:

            print ("Paquete Keep Alive con cambios")
            return desempacar_paquete_soyActivo(paquete)

        else:

            print ("Paquete Keep Alive sin cambios")
            return 0

# ------------------------
# Método para ID cuando recibe un paquete estoy aqui desde NM
# Retorna el espacio disponible del nodo
# ------------------------

def desempacar_paquete_estoyAqui(paquete):

    op_code_res = paquete[0]

    if op_code_res == 4:

        print ("Se produjo error al iniciar NM")
        return 1

    else:

        node_size = struct.unpack("=BI", paquete)
        print ("Nodo se ha reigstrado, espacio disponible: " + str(node_size[1]) + " bytes")
        return node_size[1]
