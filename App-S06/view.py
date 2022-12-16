"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

from statistics          import mode
import config as cf
import sys
import controller
from DISClib.ADT        import list as lt
from DISClib.Algorithms.Sorting import quicksort as qs
assert cf
from Clases.Model       import Model
from Clases.Station     import Station
from Clases.Rendimiento import Rendimiento
import time
from   tabulate         import tabulate
import folium
import webbrowser
import tempfile


control =  None
locations = []
#catalog = None

sys.setrecursionlimit(10000)
"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

#----------------------------------------------------------------------
#funciones para obtener la memoria
def castBoolean(value):
    """
    Convierte un valor a booleano
    """
    if value in ('True', 'true', 'TRUE', 'T', 't', '1', 1, True):
        return True
    else:
        return False

def printLoadDataAnswer(answer):
    """
    Imprime los datos de tiempo y memoria de la carga de datos
    """
    if isinstance(answer, (list, tuple)) is True:
        print("Tiempo [ms]: ", f"{answer[0]:.3f}", "||",
              "Memoria [kB]: ", f"{answer[1]:.3f}")
    else:
        print("Tiempo [ms]: ", f"{answer:.3f}")
#----------------------------------------------------------------------
#controlador

def newController():
    """
    Se crea una instancia del controlador
    """
    control = controller.newController()
    return control


def printList(lista):
    for element in lt.iterator(lista):
        print(element)


def cmpstr(a,b):
     return a < b

def getModel(control) ->Model:
    return control["model"]

#--------------------------------------------------------------------------------------------------------------------------------------------



def imprimirRuta(path, origen, destino = None):
    
    if path is None:
        print("No encontro ruta desde ",origen, end ="" )
        if destino is not None:
            print(" hasta ",destino,end="")
        print("")
        return
    
    print("Ruta desde ",origen, end ="" )
    if destino is not None:
        print(" hasta ",destino,end="")
    print("")
        
    peso = 0 
    count = 0
    transbordos = 0
    model = getModel(control)
    station = model.getStationByVertex(origen)

    locations.append([station.latitud,station.longitud])

    print("Partiendo desde ",station)
    for element in lt.iterator(path):
        station = model.getStationByVertex(element["vertexB"])
        locations.append([station.latitud,station.longitud])
        if element["vertexB"].startswith("T-"):
            print(element["vertexA"].ljust(10)," -> ",element["vertexB"].ljust(10),"Transbordo bajarse en ",station)
            transbordos += 1
        elif element["vertexA"].startswith("T-"):    
            busid = element["vertexB"].split("-")[1]
            print(element["vertexA"].ljust(10)," -> ",element["vertexB"].ljust(10),"Transbordo tomar      ","BUS-"+busid," en ",station)
        else:
            print(element["vertexA"].ljust(10)," -> ",element["vertexB"].ljust(10), station)
        peso  += element["weight"]
        count += 1
    print("Distancia Total",peso, " Numero de paradas ",count,"Transbordos:",transbordos)        


def imprimirRuta2(lista, origen, destino = None):
    if lista is None:
        print("No encontro ruta desde ",origen, end ="" )
        if destino is not None:
            print(" hasta ",destino,end="")
        print("")
        return
    
    print("Ruta desde ",origen, end ="" )
    if destino is not None:
        print(" hasta ",destino,end="")
    print("")

        
    count = 0
    transbordos = 0
    model = getModel(control)
    station = model.getStationByVertex(origen)
    locations.append([station.latitud,station.longitud])
    print("Partiendo desde ",station)
    #print(lista)
    #print("----")
    for element in lt.iterator(lista):
        #print(element)
        station = model.getStationByVertex(element)
        locations.append([station.latitud,station.longitud])
        if element.startswith("T-"):
            print(element.ljust(10),"Transbordo  ",station)
            transbordos += 1        
        else:
            print(element.ljust(10), station)        
        count += 1
    print( " Numero de paradas ",count,"Transbordos:",transbordos)        


#----------------------------------------------------------------
#              REQUERIMIENTO 0 
#----------------------------------------------------------------

def requerimiento_0():
    print("Cargando información de los archivos ....")
    file_size = input("\nSeleccione el tamaño de la muestra:\n5pct\n10pct\n20pct\n30pct\n50pct\n80pct\nlarge\nsmall\n Seleccione una opción para continuar: ")
    
    print("Desea observar el uso de memoria? (True/False)")
    mem = input("Respuesta: ")
    mem = castBoolean(mem)

    answer = controller.Tiempo_de_carga_loadData(file_size, control, memflag=mem)
    printLoadDataAnswer(answer)
    model = getModel(control) 
    print("Estaciones de Bus - Bus Stops")
    totalBusStops , exclusiveBusStops , sharedBusStops = model.estadisticaCarga()
    print("Numero de estaciones de exclusivas :" ,exclusiveBusStops)
    print("Numero de estaciones de transbordo :" , sharedBusStops)
    print("Total de Estaciones:                ", totalBusStops)

    print("Rutas de Bus")
    print("Numero total de rutas de bus:      " , model.getBusRoutesSize())
    ####print("-----------------------[rutas]-------------------")
    ###printList(model.getBusRoutesList())


    #print(lt.size(lista_stops))
    ###print("-----------------------[vertces del grafo]-------------------")
    ###vertices_lt = model.getGraphVertexList()
    ###vertices_lt = qs.sort(vertices_lt,cmpstr)
    ###printList(vertices_lt)
    vertices = model.getGraphVertexList()
    print("numero vertices grafo:            ",lt.size(vertices))
    ###print("-----------------------[arcos del grafo]-------------------")
    ###printList(model.getGraphEdgesList())

    ###edges = model.getGraphEdgesList()    
    ###for e in lt.iterator(edges):
    ###    print(e["vertexA"]+","+str(round(e["weight"],2)) +", "+e["vertexB"])
    print("numero arcos grafo:               ",lt.size(model.getGraphEdgesList()))

    lat_min,lon_min, lat_max, lon_max = model.rectanguloBarcelona()
    print("latitud min",lat_min,"longitud min",lon_min, "latitud max",lat_max,"longitud max", lon_max)
    #lista = model.getStationsList()
    pr5 = print_primeros_y_ultimos(vertices,None, 5, True)
    print_vertices_req0(pr5)

def print_vertices_req0(lista):
    model = getModel(control)   
    headers = [ "Node", "Codigo", "BusID","Latitud","Longitud"]
    impresion = []        
    
    for vertice in lt.iterator(lista):
        station = model.getStationByVertex(vertice)
        impresion.append([vertice, station.code,"BUS-"+vertice.split("-")[1],station.latitud, station.longitud, model.indegree(vertice)])        

        
    print(tabulate(impresion, headers, tablefmt="grid"))

def print_primeros_y_ultimos(lista, funcion_de_impresion, num, True_or_False):
    
    #Entra si es True
    if True_or_False:
        if lt.size(lista) > num*2:
            primeros = lt.subList(lista, 1, num)
            ultimos  = lt.subList(lista, lt.size(lista)-(num-1), num)
            for line in lt.iterator(ultimos):
                lt.addLast(primeros, line )  
                if funcion_de_impresion:               
                    funcion_de_impresion(primeros)
            return primeros
        else:
            if funcion_de_impresion:    
                funcion_de_impresion(lista)
            return lista

    #Entra si es False
    else: 
        if lt.size(lista) > num:
            total = lt.subList(lista, 1, num)
            funcion_de_impresion(total)
            return total
        else:
            funcion_de_impresion(lista)
            return lista


#----------------------------------------------------------------------
def printMenu():
    print()
    print("===========================")
    print("       Bienvenido")
    print("")
    print("0- Cargar información desde los Archivos")
    print("1- (REQ 1)Buscar un camino posible entre dos estaciones")
    print("2- (REQ 2)Buscar el camino con menos estaciones entre dos estaciones")
    print("3- (REQ 3 INDIVIDUAL)Reconocer los componentes conectados de la Red de rutas de bus")
    print("4- (REQ 4 INDIVIDUAL)Planear el camino con distancia mínima entre dos puntos geográficos")
    print("5- (REQ 5 INDIVIDUAL)Localizar las estaciones “alcanzables” desde un origen a un número máximo de conexiones dado")
    print("6- (REQ 6 INDIVIDUAL)Buscar el camino con distancia mínima entre una estación de origen y un vecindario de destino")
    print("7- (REQ 7 INDIVIDUAL)Encontrar un posible camino circular desde una estación de origen")
    print("8- (REQ 8 BONO)Graficar resultados para cada uno de los requerimientos")


def print_Requerimiento_3(lista):
    impresion_req3 = []
    headers = [ "numero de estaciones", "indices"]
    for element in lt.iterator(lista):
        vertices =print_primeros_y_ultimos( element["vertices"] , None, 3, True)
        new_vertice = ""
        for vertice in lt.iterator(vertices):
            new_vertice = new_vertice +", " + vertice
        impresion_req3.append([ element["cont"],new_vertice[1:] ])
        
    print(tabulate(impresion_req3, headers, tablefmt="grid"))


while True:
    printMenu()
    opcion = None
    try:
        opcion = int(input('Seleccione una opción para continuar\n'))
    except:
        opcion = -1
    if int(opcion) == 0:
        control = newController()
        modelClass = control["model"]
        requerimiento_0()
    elif opcion == 1:
        
        origen = input("Identificador de la estación origen:   ")
        destino = input("Identificador de la estación destino: ")
        rendimiento = Rendimiento(True)
        cola, peso = controller.requerimiento_1(modelClass, origen, destino)
        rendimiento.finalizar()
        imprimirRuta(cola,origen,destino)
        #print("La distancia del recorrido es de", peso)
        

    elif opcion == 2:
        
        origen  = input("Identificador de la estación origen:  ")
        destino = input("Identificador de la estación destino: ")

        rendimiento = Rendimiento(True)
        cola, peso = controller.requerimiento_2(modelClass, origen, destino)
        rendimiento.finalizar()

        imprimirRuta2(cola,origen,destino)
        
    elif opcion == 3:

        rendimiento = Rendimiento(True)
        lista_valores, num_conected = controller.requerimiento_3(modelClass)
        rendimiento.finalizar()

        print_primeros_y_ultimos( lista_valores , print_Requerimiento_3, 5, False)

    elif opcion == 4:
        print('Localización geográfica del usuario')
        lonOrigen  = float(input("Origen (longitud) del usuario': "))
        latOrigen  = float(input("Origen (latitud)  del usuario': "))
        lonDestino = float(input("Destino(longitud) del usuario': "))
        latDestino = float(input("Destino(latitud)  del usuario': "))

        rendimiento = Rendimiento(True)
        cola, peso, origen, destino = controller.requerimiento_4(modelClass, lonOrigen, latOrigen, lonDestino, latDestino)
        rendimiento.finalizar()

        imprimirRuta(cola,origen,destino)

    elif opcion == 5:
        pass
    elif opcion == 6:

        vertice_origen = str(input("Identificador de la estación origen (en formato Code-IdBus): "))
        vecindario_destino = str(input("El identificador del vecindario (Neighborhood) destino: "))
        if not getModel(control).containsVertex(vertice_origen) :
            print("Estacion de origen no existe")
        else:
            rendimiento = Rendimiento(True)
            cola, peso, largo= controller.requerimiento_6(modelClass, vertice_origen, vecindario_destino)
            rendimiento.finalizar()

            imprimirRuta(cola, vertice_origen, vecindario_destino)

    elif opcion == 7:
        vertice_origen = str(input("Identificador de la estación origen (en formato Code-IdBus): "))
        ###modelClass.cycles(vertice_origen)
        cola  = controller.requerimiento_7(modelClass, vertice_origen)
        imprimirRuta2(cola,vertice_origen)
    elif opcion == 8:
        m = folium.Map(locations[0], zoom_start=16)
        my_PolyLine=folium.PolyLine(locations=locations,weight=5)
        m.add_child(my_PolyLine)
        ruta = tempfile.gettempdir()+("/graph.html")
        m.save(ruta)
        webbrowser.open("file://"+ruta)
        pass
        
    elif opcion == -1:
        print("Opción inválida")
        #sys.exit(0)
sys.exit(0)
