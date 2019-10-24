import os
import struct

class AdministradorMem:

    def __init__(self):
        self.memoriaPrincipal = [bytearray(200000),bytearray(2500)]

        self.contadorPaginas = self.cargarContPaginas()
        self.tablaPaginas = self.cargarTablaPaginas()
        self.colaPaginas = [[],[]]
        
        if not os.path.isdir("paginas"):
            os.makedirs("paginas")

    def pagEstaEnPrincipal(self,numPagina):
        esta = True
        if ( self.tablaPaginas[numPagina]==-1):
            esta = False

        return esta

    def getMemPrinLlena(self, tamano):
        llena = False
        if (len(self.colaPaginas[tamano]) == 5):
            llena = True

        return llena

    def getPaginaPorCambiar(self, tamano):
        return self.colaPaginas[tamano].pop()

    def cargarContPaginas(self):
        contador = 0
        ultimaPagEncontrada = False
        while not ultimaPagEncontrada:
            try:
                archivo = open("paginas/" + str(contador) + ".txt","r")
                contador+=1
            except:
                ultimaPagEncontrada = True

        print(contador)
        return contador

    def cargarTablaPaginas(self):
        tabla = []
        for i in range(self.contadorPaginas):
            tabla.append(-1)

        return tabla

    def enviarPagMemSecundaria(self, tamano, numPagina):
        busDatos = bytearray(1)
        if (tamano == 0):
            busDatos = bytearray(40000)
        else:
            busDatos = bytearray(500)

        posicion = self.tablaPaginas[numPagina]
        for i in range(len(busDatos)):
            busDatos[i] = self.memoriaPrincipal[tamano][posicion+i]

        archivo = open("paginas/" + str(numPagina) + ".txt","w+b")

        archivo.write(busDatos)
        self.tablaPaginas[numPagina] = -1
        self.vaciarPagina(tamano,posicion)
        archivo.close()

    def cargarPagMemSecundaria(self,tamano,numPagina,posicion):
        nombreArchivo = "paginas/" + str(numPagina) + ".txt"
        archivo = open(nombreArchivo, "rb")
        busDatos = bytearray(archivo.read())
        os.remove(nombreArchivo)

        longitud = 0
        if (tamano == 0):
            longitud = 40000
        else:
            longitud = 500

        for i in range(posicion,posicion+longitud):
            self.memoriaPrincipal[tamano][i] = busDatos[i-posicion]

        self.tablaPaginas[numPagina]= posicion
        archivo.close()

    def vaciarPagina(self,tamano,posicion):
        longitud = 0
        if (tamano == 0):
            longitud = 40000
        else:
            longitud == 500

        for i in range (posicion,posicion+longitud):
            self.memoriaPrincipal[tamano][i] == 0x00

    def buscarPosicionVacia(self,tamano):
        posicion = 0
        incremento = 0
        if tamano == 0:
            incremento = 40000
        else:
            incremento = 500

        encontrada = False
        while not encontrada:
            if posicion in self.tablaPaginas:
                posicion += incremento
            else:
                encontrada = True

        return posicion

    def swapPaginas(self,tamano,pagNueva):
        pagVieja = self.getPaginaPorCambiar(tamano)
        posicion = self.tablaPaginas[pagVieja]
        self.enviarPagMemSecundaria(tamano,pagVieja)

        self.cargarPagMemSecundaria(tamano,pagNueva,posicion)
        self.colaPaginas[tamano].insert(0,pagNueva)

        return posicion

    def leerUnDato(self,tamano,posicion,tamanoDato,formato):
        datoBytes = bytearray(tamanoDato)
        for k in range (tamanoDato):
            datoBytes[k] = self.memoriaPrincipal[tamano][posicion+k]

        datoReal = 0
        if(tamano == 0):
            if(formato==0):
                datoReal = struct.unpack('Ii', datoBytes)
            else:
                datoReal = struct.unpack('If', datoBytes)
        else:
            datoReal = struct.unpack('IB', datoBytes)

        return datoReal[0], datoReal[1]

    """
    --------------------------------------------------------------------------------------------------------
    Funciones a utilizar en Interfaz
    --------------------------------------------------------------------------------------------------------
    """

    """
    Funcion que guarda un dato dado por la interfaz.
    Parametros:
        -tamano: El tamano de la pagina donde se va a guardar el dato.
            tamano = 0 : Paginas de 40KB
            tamano = 1 : Paginas de 0.5KB
        -numPagina: Numero de pagina donde se quiere guardar el dato.
        -offset: Corrimiento a partir del inicio de la pagina seleccionada
                 donde se quiere guardar el dato.
        -dato: Dato a guarda en la recibido en forma de bytes o bytearray.
    """
    def guardarDato(self,tamano,numPagina,offset,dato):
        posicion = -1
        if (self.pagEstaEnPrincipal(numPagina)):
            posicion = self.tablaPaginas[numPagina]

        else:
            posicion = self.swapPaginas(tamano,numPagina)

        desplaz = 0
        if tamano == 0:
            desplaz = 8
        else:
            desplaz = 5

        posicion += offset
        for i in range (posicion,posicion+desplaz):
            self.memoriaPrincipal[tamano][i] = dato[i-posicion]

    """
    Funcion reserva una pagina en memoria y devuelve el numero de pagina.
    Parametros:
        -tamano: Tamano de la pagina que se quiere reservar.
            tamano = 0 : Paginas de 40KB
            tamano = 1 : Paginas de 0.5KB
    Retorno:
        -pagAsignada: Numero de pagina quue fue asignada con el llamado a
                      la funcion.
    """
    def reservarPagina(self,tamano):
        posicion = 0
        if self.getMemPrinLlena(tamano):
            paginaCambiar = self.getPaginaPorCambiar(tamano)
            posicion = self.tablaPaginas[paginaCambiar]
            self.enviarPagMemSecundaria(tamano,paginaCambiar)
        else:
            posicion = self.buscarPosicionVacia(tamano)

        self.tablaPaginas.append(posicion)
        self.colaPaginas[tamano].insert(0,self.contadorPaginas)
        pagAsignada = self.contadorPaginas
        self.contadorPaginas+=1

        return pagAsignada


    """
    Funcion que devuelve todos los datos de todas las paginas pedidas hasta
    el offset de la ultima pagina en la lista.
    Parametros:
        -tamano: Tamano de las paginas a consultar.
            tamano = 0 : Paginas de 40KB
            tamano = 1 : Paginas de 0.5KB
        -listaPaginas: Lista de todas las paginas que se quieren consultar.
        -offsetUltPag: offset de la ultima pagina en la lista para evitar copiar
                       todos los ceros que puede tener la ultima pagina si esta
                       medio llena.
                       >Si tamano = 0: offset <= 40000 y multiplos de 8.
                       >Si tamano = 1: offset <= 500 y multiplos de 5.
        -formato8Bytes: Indicador del tipo de datos que se devuelve de las paginas
                        de 40KB. Este no tiene ningun efecto cuando las paginas
                        son de 0.5KB.
            formato8Bytes = 0 : Datos enteros
            formato8Bytes = 1 : Datos de punto flotante.
    Retorno:
        -busDatos: Lista con todos los datos solicitados de la forma
                   fecha-dato-fecha-dato...
    """
    def obtenerDatos(self,tamano,listaPaginas,offsetUltPag,formato8Bytes):
        tamanoPagina = 0
        tamanoDato = 0
        if (tamano == 0):
            tamanoPagina = 40000
            tamanoDato = 8
        else:
            tamanoPagina = 500
            tamanoDato = 5

        busDatos = []

        for i in range (len(listaPaginas)-1):
            if self.pagEstaEnPrincipal(listaPaginas[i]):
                posicion = self.tablaPaginas[listaPaginas[i]]
            else:
                posicion = self.swapPaginas(tamano,listaPaginas[i])

            for j in range (posicion,posicion+tamanoPagina,tamanoDato):
                fecha , dato = self.leerUnDato(tamano,j,tamanoDato,formato8Bytes)
                busDatos.append(fecha)
                busDatos.append(dato)

        if self.pagEstaEnPrincipal(listaPaginas[-1]):
            posicion = self.tablaPaginas[listaPaginas[-1]]
        else:
            posicion = self.swapPaginas(tamano,listaPaginas[-1])

        for j in range(posicion,posicion+offsetUltPag,tamanoDato):
            fecha , dato = self.leerUnDato(tamano,j,tamanoDato,formato8Bytes)
            busDatos.append(fecha)
            busDatos.append(dato)

        return busDatos

    """
    Funcion que guarda todas las paginas actualmente presentes en memoria principal
    en caso que se haga un Ctrl+C desde Interfaz para proteger los datos.
    """
    def salvarMemPrincipal(self):
        for i in range (len(self.tablaPaginas)):
            if i in self.colaPaginas[0]:
                self.enviarPagMemSecundaria(0,i)
            elif i in self.colaPaginas[1]:
                self.enviarPagMemSecundaria(1,i)

        print("Todas las paginas en memoria principal fueron guardadas en memoria secundaria.")
