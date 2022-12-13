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

import config as cf
import sys
import controller
from DISClib.ADT import list as lt
from prettytable import PrettyTable
assert cf
import time
import tracemalloc
import csv

csv.field_size_limit(2147483647)
default_limit = 1000
sys.setrecursionlimit(default_limit*10)

edgesfile = '/Challenge-4/Barcelona/bus_edges_bcn-utf8-small.csv'
stopsfile = '/Challenge-4/Barcelona/bus_stops_bcn-utf8-small.csv'
"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("Bienvenido")
    print("0- Cargar información en el catálogo")
    print("1- Buscar un camino posible entre dos estaciones")
    print("2- Buscar el camino con menos paradas entre dos estaciones")
    print("3- Reconocer los componentes conectados de la Red de rutas de bus")
    print("4- Planear el camino con distancia mínima entre dos puntos geográficos")
    print("5- Informar las estaciones \"alcanzables\" desde un origen a un número máximo de conexiones")
    print("6- Buscar el camino con mínima distancia entre una estación de origen y un vecindario de destino")
    print("7- Encontrar un posible camino circular desde una estación de origen")
    print("8- Graficar resultados para cada uno de los requerimientos")

    
catalog = None
def printEleccionArchivo1():
    '''O(1)'''
    print("\nElija el tamaño de archivo que desea cargar")
    print("1- small")
    print("2- 05pct")
    print("3- 10pct")
    print("4- 20pct")
    print("5- 30pct")
    print("6- 50pct")
    print("7- 80pct")
    print("8- large")

def getTime():
    '''O(1)'''
    return float(time.perf_counter()*1000)

def deltaTime(start, end):
    '''O(1)'''
    elapsed = float(end - start)
    return elapsed

def printCarga(primlast):
    x = PrettyTable()
    x.field_names = ["Nombre de estación", "Codigo", "Bus_Stop","Transport", "Longitude", "Latitude","District_Name", "Neighborhood", "Adyacentes"]
    x.max_width=20
    x.hrules = True
    x.align="l"
    for p in lt.iterator(primlast):
        x.add_row([p['ID'],p['Code'],p['Bus_Stop'], p['Transport'], p['Longitude'], p['Latitude'], p['District_Name'], p['Neighborhood_Name'], p['adjacent']])
    print(x)

def printReq1(origen, destino, cont):
    x = PrettyTable()
    x.field_names = ["Vertice de salida ", "Vertice de llegada", "Peso"]
    x.max_width=20
    x.hrules = True
    x.align="l"

    existe, dic = controller.req1(origen, destino, cont) 
    if existe:
        print("Distancia total: ", dic['costo'])
        print("Total de estaciones: ", dic['tamano'])
        print("Total de transbordos: ", dic['transbordo'])
        print("Camino: ")
        for i in lt.iterator(dic['camino']):
            x.add_row([i['vertexA'], i['vertexB'], i['weight']])
        print(x)
    else:
        print("No existe un camino entre estas estaciones. ")

def printReq2(origen, destino, cont):
    x = PrettyTable()
    x.field_names = ["Vertice de salida ", "Vertice de llegada", "Peso"]
    x.max_width=20
    x.hrules = True
    x.align="l"

    existe, dic = controller.req2(origen, destino, cont) 
    if existe:
        print("Distancia total: ", dic['costo'])
        print("Total de estaciones: ", dic['tamano'])
        print("Total de transbordos: ", dic['transbordo'])
        print("Camino: ")
        for i in lt.iterator(dic['camino']):
            x.add_row([i['vertexA'], i['vertexB'], i['weight']])
        print(x)
    else:
        print("No existe un camino entre estas estaciones. ")

def printReq4(loc_origen, loc_destino, cont):
    origen = loc_origen.strip().split(',')
    destino = loc_destino.strip().split(',')
    origen = {'Latitude':origen[1],'Longitude':origen[0]}
    destino = {'Latitude':destino[1],'Longitude':destino[0]}
    existe, dic = controller.req4(origen, destino,cont)
    print('La estación más cercana al origen es {} y está a una distancia de {}'.format(dic['origen'],dic['d_org']))
    print('La estación más cercana al destino es {} y está a una distancia de {}'.format(dic['destino'],dic['d_des']))
    if existe:
        
        print('La distancia total que tomará el recorrido entre {} y {} es: {}'.format(dic['origen'],dic['destino'],dic['costo']))
        print('Se pasa por {} estaciones en total.'.format(dic['tamano']-dic['transbordo']))
        print('Se hacen {} transbordos.'.format(dic['transbordo']))
        ojito = [i for i in lt.iterator(dic['camino'])]
        if len(ojito) != 0:
            camino_recorrido = [(ojito[0]['vertexB'].split('-')[0],0)]
            camino_recorrido += [(i['vertexA'].split('-')[0],i['weight']) for i in ojito if i['weight']>0]
            print('El camino a recorrer es:')#.format(camino_recorrido))
            x = PrettyTable()
            x.field_names = ["Estación ", "Siguiente", "Distance_Next"]
            x.max_width=20
            x.hrules = True
            x.align="l"
        
            for i in lt.iterator(dic['camino']):
                x.add_row([i['vertexA'], i['vertexB'],i['weight']])
            print(x)
        #camino_recorrido += [(i['vertexA'],i['weight']) for i in ojito if 'T-'not in i['vertexA']]
        else:
            camino_recorrido = ojito
        
        #print(len(ojito),len(camino_recorrido))

def printReq5(origen,n,cont):
    data = controller.req5(origen,n,cont)
    rout = str(origen.split('-')[1])
    if len(data) > 0:
        x = PrettyTable()
        x.field_names = ["Estación", "Longitud", "Latitud", "Saltos", "Distancia"]
        x.max_width=25
        x.hrules = True
        x.align="l"
        for i in data:
            #print("i", i)
            estacion = i['destino'] + "-" + rout
            print(estacion)
            x.add_row([estacion, i['info']['Longitude'], i['info']['Latitude'], i['saltos'], i['costo']])
        print(x)

def printReq6(origen,vecindario_destino,cont):
    dic = controller.req6(origen,vecindario_destino,cont)
    if dic is None:
        print('No hay camino')
    else:
        print("El camino de distancia mínimo entre la estación {} y el vecindario {}".format(origen, vecindario_destino))
        print("Distancia total: ", dic['costo'])
        print("Total de estaciones: ", dic['tamano'])
        print("Total de transbordos: ", dic['transbordo'])
        print("Camino calculado: ")
        
        x = PrettyTable()
        x.field_names = ["Estación", "Vecindario actual", "Siguiente estación", "Distancia"]
        x.max_width=25
        x.hrules = True
        x.align="l"
        lst = list(lt.iterator(dic['camino']))
        lst.reverse()
        #print(lst)
        for i in lst:
           stop = controller.getStopFromList(cont, i['vertexA'])
           x.add_row([i['vertexA'],stop['Neighborhood_Name'], i['vertexB'], i['weight']])
        print(x)
        #print(dic.keys)
        #print(dic)
        #prueba en 80pct 833-V21 la Salut

def printReq7(origen, camino):
    dist = 0
    transbordo = 0
    estaciones = 0
    for est in camino:
        dist += float(est['weight'])
        if "T" in est['vertexB']:
            transbordo += 1
        else:
            estaciones += 1
    
    #if dist == 0 or estaciones <= 1:
    #    print("No hay camino circular posible")
    #else:
    print("La distancia total es: ", dist)
    print("Total de estaciones: ", estaciones)
    print("Total de transbordos: ", transbordo)
    print("El camino calculado es: ")
    x = PrettyTable()
    x.field_names = ["Estación ", "Siguiente estación", "Distancia"]
    x.max_width=20
    x.hrules = True
    x.align="l"
    
    if camino != None:
        
        for j in camino:  
            x.add_row([j['vertexA'], j['vertexB'], j['weight']])
        print(x)
"""
Menu principal
"""
while True:
    print('\n'*2 + '-'*30)
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 0:
        start_time = getTime()
        
        cont = controller.init()

        printEleccionArchivo1()
        input_archivo = input('Seleccione una opción para continuar\n')
        if input_archivo == "1":
            id = "small"
        elif input_archivo == "2":
            id = "5pct"
        elif input_archivo == "3":
            id = "10pct"
        elif input_archivo == "4":
            id = "20pct"
        elif input_archivo == "5":
            id = "30pct"
        elif input_archivo == "6":
            id = "50pct"
        elif input_archivo == "7":
            id = "80pct"
        elif input_archivo == "8":
            id = "large"
        else:
            print("\nDebe elegir una opción válida\n")
            break

        load = controller.loadData(cont, id)
        print("Cargando información de los archivos ....")
        #print(cont["Bus_routes"])
        #totalroutes = controller.getTotalRoutes(cont)
        totalroutesExclus = controller.getTotalRoutesExclus(cont)
        totalparadas = controller.getTotalTransbordo(cont)
        arcos = controller.getEdges(cont)
        minlat = controller.getMinlat(cont)
        minlon = controller.getMinlon(cont)
        maxlat = controller.getMaxlat(cont)
        maxlon = controller.getMaxlon(cont)
        vertices = lt.size(controller.getVertex(cont))
        primlast = controller.getFirstLast(load[1], load[0])
        #print("Número total de rutas de buses: ", totalroutes)
        print("Número de estaciones compartidas: ", totalparadas)
        print("Número de estaciones exclusivas: ", totalroutesExclus)
        print("Número de estaciones total: ", (totalroutesExclus + totalparadas))
        print("Número de arcos: ", arcos)
        print("\n Número de vertices: ", vertices)
        print("Rango de área: ")
        print("  Min longitude: ", minlon, " Max longitude: ", maxlon)
        print("  Min latitude: ", minlat, " Max latitude: ", maxlat)
        printCarga(primlast)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))

        #print(cont['stops'])
        #print(cont['stopMap'])
        #print(cont['paradas'])
        #print(cont['latitude'])
        #print(cont['longitude'])
        #print(cont['stopVertex'])
    
    elif int(inputs[0]) == 1:
        start_time = getTime()
        origen = input("Ingrese el identificador de las estación de origen: ")
        destino = input("Ingrese el identificador de las estación de destino: ")
        printReq1(origen, destino, cont)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))

    elif int(inputs[0]) == 2:
        start_time = getTime()
        origen = input("Ingrese el identificador de las estación de origen: ")
        destino = input("Ingrese el identificador de las estación de destino: ")
        printReq2(origen, destino, cont)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))

    elif int(inputs[0]) == 4:
        start_time = getTime()
        print('Los inputs de este requerimiento deben llevar el formato: Longitud,Latitud')
        loc_origen = input('Localización geográfica de origen: ')
        loc_destino = input('Localización geográfica de destino: ')
        printReq4(loc_origen,loc_destino,cont)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))

    elif int(inputs[0]) == 5:
        start_time = getTime()
        origen = input('Identificador de la estación de origen (Code-IdBus): ')
        n = int(input('Número máximo de conexiones: '))
        printReq5(origen,n,cont)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))

    elif  int(inputs[0]) == 6:
        start_time = getTime()
        origen = input('Identificador de la estación de origen (Code-IdBus): ')
        vecindario_destino = input('Nombre del vecindario destino: ')
        printReq6(origen,vecindario_destino,cont)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))
    
    elif int(inputs[0]) == 7:
        start_time = getTime()
        origen = input("vertice de origen: ")
        camino = controller.req7(cont, origen)
        #printReq7(origen, controller.req7(cont, origen))
        printReq7(origen, camino)

        end_time = getTime()
        delta_time = deltaTime(start_time, end_time)
        print("Delta tiempo requerimiento: {}".format(delta_time))


    else:
        sys.exit(0)
sys.exit(0)
