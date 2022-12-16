"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as ss
from tabulate import tabulate
import controller
import datetime 
import time
import copy
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import orderedmap as om
from DISClib.ADT import minpq as pq
from DISClib.ADT import stack as st
from DISClib.ADT import graph as gr
from DISClib.ADT import indexminpq as ipq
import folium
from folium.plugins import MarkerCluster
import math
assert cf
from DISClib.Algorithms.Sorting import mergesort as ms
import sys
from prettytable import PrettyTable as ptbl
from DISClib.Algorithms.Graphs import dfs
from DISClib.Algorithms.Graphs import bfs
from DISClib.Algorithms.Graphs import dijsktra as dj
from DISClib.Algorithms.Graphs import scc 
from DISClib.Algorithms.Graphs import cycles as cy 


#para intalar harvesine ejecutar en consola:               pip install haversine
from haversine import haversine, Unit



"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    """
    Se crea el analizador de los datos del reto
    
    """    
    
    analyzer = {"DiGraph": None,
                "graph": None,
                "id->Coordenadas HASH": None,
                "id->District_Name HASH":None,
                "id->Neighborhood_Name HASH":None,
                "neighborgoodByCodeStation":None,
                "hashPerNeighborhood":None,
                "Arcos LIST": None,
                "Vertices LIST": None,
                "Totales HASH": None,
                "rutas LIST": None,
                "listPerTransbordo": None,
                "listPerNOTTransbordo": None,
                "mapa de longitudes": None,
                "mapa de latitudes": None
                }
    
    #Tiene el cálculo exacto para el tamaño sumando el total de busstops + transbordos
    analyzer["DiGraph"] = gr.newGraph(datastructure="ADJ_LIST", directed=True, size=5011, comparefunction=compareStopIds)
    analyzer["graph"] = gr.newGraph(datastructure="ADJ_LIST", directed=False, size=5011, comparefunction=compareStopIds)

    #Tiene el número de elementos preciso, es decir, el número primo más cercano al producto del total de bustops x 4
    analyzer["id->Coordenadas HASH"] = mp.newMap(numelements=18593, maptype='PROBING', loadfactor=0.5, comparefunction=compareMapID)
    analyzer["id->District_Name HASH"] = mp.newMap(numelements=18593, maptype='PROBING', loadfactor=0.5, comparefunction=compareMapID)
    analyzer["hashPerNeighborhood"] = mp.newMap(numelements=18593, maptype='PROBING', loadfactor=0.5, comparefunction=compareMapID)
    analyzer["id->Neighborhood_Name HASH"] = mp.newMap(numelements=18593, maptype='PROBING', loadfactor=0.5, comparefunction=compareMapID)
    analyzer["neighborgoodByCodeStation"] = mp.newMap(numelements=18593, maptype='PROBING', loadfactor=0.5, comparefunction=compareMapID)

    analyzer["rutas LIST"] = lt.newList(cmpfunction=compareList)
    analyzer["listPerTransbordo"] = lt.newList(cmpfunction=compareList)
    analyzer["listPerNOTTransbordo"] = lt.newList(cmpfunction=compareList)

    analyzer["mapa de longitudes"] = om.newMap('BST', compareList)
    analyzer["mapa de latitudes"] = om.newMap('BST', compareList)

    #analyzer["Arcos LIST"] = lt.newList(datastructure='ARRAY_LIST', cmpfunction= ?????????? va a ser una lista literal solo de los pesos de los vértices? o que?)
    #analyzer["Vertices LIST"] = lt.newList(datastructure='ARRAY_LIST', cmpfunction= ?????? va a ser lit de solo los identificadores? pa que? toca preguntar)

    return analyzer

# Funciones para agregar informacion al catalogo

def addCoordenadasToHASH(stop, analyzer):
    map = analyzer["id->Coordenadas HASH"]
    longitude = stop["Longitude"]
    latitude = stop["Latitude"]
    id = stop["id"]

    mp.put(map, id, (latitude, longitude))

    if stop["Transbordo"] == "S":
        newid = "T-"+ stop["Code"]
        mp.put(map, newid, (latitude, longitude))

def addDistrictToHASH(stop, analyzer):
    map = analyzer["id->District_Name HASH"]
    district = stop["District_Name"]
    id = stop["id"]

    mp.put(map, id, district)

    if stop["Transbordo"] == "S":
        id = "T-"+ stop["Code"]
        mp.put(map, id, district)

def addNeighToHASH(stop, analyzer):
    map = analyzer["id->Neighborhood_Name HASH"]
    map2 = analyzer["neighborgoodByCodeStation"]
    neigh = stop["Neighborhood_Name"]
    id = stop["id"]
    stationCode = (stop["id"].split("-"))
    stationCode = stationCode[0]

    mp.put(map, id, neigh)
    if not(mp.contains(map2,stationCode)):
        mp.put(map2, stationCode, neigh)

    if stop["Transbordo"] == "S":

        id = "T-"+ stop["Code"]
        mp.put(map, id, neigh)

def addNeighborhoodToHASH(stop, analyzer):
    map = analyzer["hashPerNeighborhood"]
    id = stop["id"]
    neighborhood = stop["Neighborhood_Name"]
    if not(mp.contains(map,neighborhood)):
        listita= lt.newList(cmpfunction=compareList)
        mp.put(map,neighborhood,listita)
    listaBarrios = getValueFast(map, neighborhood)
    if not(lt.isPresent(listaBarrios,id)):
        lt.addLast(listaBarrios,id)

def addVertexToGraph(stop, graph, analyzer):
    id = stop["id"]
    coso = stop["id"].split("-")
    transbordo = "T-"+coso[0]
    graph = analyzer[graph]
    if stop["Transbordo"]=="S":
        if not(gr.containsVertex(graph, transbordo)):
            gr.insertVertex(graph=graph, vertex=transbordo)
        if not(lt.isPresent(analyzer["listPerTransbordo"],transbordo)):
            lt.addLast(analyzer["listPerTransbordo"],transbordo)
    else:
        coso = stop["id"].split("-")
        idEstacion = coso[0]
        if not(lt.isPresent(analyzer["listPerNOTTransbordo"],idEstacion)):
            lt.addLast(analyzer["listPerNOTTransbordo"],idEstacion)


    gr.insertVertex(graph=graph, vertex=id)

def ordenarListasExperimento (analyzer):
    print("Voy a ordenar")
    ms.sort(analyzer["listPerNOTTransbordo"],cmpRutas)
    ms.sort(analyzer["listPerTransbordo"],cmpRutas)
    print("Ya ordené, god")

def addEdgeToTransbordo (stop, graph, analyzer):
    graph = analyzer[graph]
    id = str(stop["id"])
    transbordoCode = "T-"+str(id[0:4])
    gr.addEdge(graph, id, transbordoCode, 0.0)
    gr.addEdge(graph, transbordoCode, id, 0.0)

def addEdgesToGraph(edge, graph, analyzer):
    graph = analyzer[graph]
    coso = edge["Bus_Stop"].split("-")
    bus =coso[1]
    vertexA = edge["Code"] + "-" + bus
    vertexB = edge["Code_Destiny"] + "-" + bus
    coorA = getValueFast(analyzer["id->Coordenadas HASH"], vertexA)
    coorB = getValueFast(analyzer["id->Coordenadas HASH"], vertexB)
    weight = haversine(coorA, coorB)
    

    gr.addEdge(graph, vertexA, vertexB, weight)
    if graph =="DiGraph":
        gr.addEdge(graph, vertexB, vertexA, weight)
    
def addCoord(coor, map):
    om.put(map, coor, None)
# Funciones para creacion de datos

# Funciones de consulta


#! =^..^=   =^..^=   =^..^=    =^..^=  [FUNCIÓN DE IMPRESIÓN (creo)]  =^..^=    =^..^=    =^..^=    =^..^=

def intentoPrinteador(stackDado, graph, req7=None):
    totalTransbordos = 0
    path = lt.newList(cmpfunction=compareList)
    totalDistance = 0
    while not(st.isEmpty(stackDado)):
        stop = st.pop(stackDado)
        if req7==None:
            if stop[0] == "T":
                totalTransbordos += 1
                nextStop = st.top(stackDado)
                stop = stop + f" -- Realiza transbordo a la ruta ({nextStop})"
                lt.addLast(path, stop)

            elif st.size(stackDado) > 0:
                nextStop = st.top(stackDado)
                if nextStop[0] == "T":
                    stop = stop + f" !! Parada en estación de transbordo ({nextStop})"
                    lt.addLast(path, stop)

                else:
                    edge = gr.getEdge(graph, stop, nextStop)
                    distance = edge['weight']
                    totalDistance += distance
                    stop = stop + f" -> Distancia a la siguiente parada ({nextStop}): {round(distance, 2)} Km"
                    lt.addLast(path, stop)

            else:
                stop = stop + " < Destino"
                lt.addLast(path, stop)
        else:
            if stop[0] == "T":
                totalTransbordos += 1
                nextStop = st.top(stackDado)
                stop = stop + f" -- Realiza transbordo a la ruta ({nextStop})"
                lt.addLast(path, stop)

            elif st.size(stackDado) > 0:
                nextStop = st.top(stackDado)
                if nextStop[0] == "T":
                    stop = stop + f" !! Parada en estación de transbordo ({nextStop})"
                    lt.addLast(path, stop)

                else:
                    edge = gr.getEdge(graph, stop, nextStop)
                    distance = edge['weight']
                    totalDistance += distance
                    stop = stop + f" -> Distancia a la siguiente parada ({nextStop}): {round(distance, 2)} Km"
                    lt.addLast(path, stop)

            else:
                edge = gr.getEdge(graph, stop, req7)
                distance = edge['weight']
                totalDistance += distance
                if req7[0] == "T":
                    stop = stop + f" !! Parada en estación de transbordo ({req7})"
                    lt.addLast(path, stop)
                else:
                    stop = stop + f" -> Distancia a la siguiente parada ({req7}): {round(distance, 2)} Km"
                    lt.addLast(path, stop)
    for stop in lt.iterator(path):
        print(">>> " + stop)
        if (stop[11:] == "Destino"):
            print("\n")
    if req7!=None:
        print(f"Hemos llegado a {req7}, volvimos a donde empezamos, ¡Es una ruta circular!")
    return totalTransbordos,totalDistance

def printeadorReqCuatro(stackDado, analyzer=None):
    if analyzer!=None:
        map = analyzer["neighborgoodByCodeStation"]
    textote = ""
    transbordo = 0
    while not(st.isEmpty(stackDado)):
        stop = st.pop(stackDado)
        verticeA = stop["vertexA"]
        verticeB = stop["vertexB"]
        if verticeB[0]=="T":
            transbordo+=1
        peso = stop["weight"]
        textote += f"para ir de {verticeA} --> {verticeB} necesitas recorrer {round(peso,2)}KM"
        if analyzer!=None:
            busStationB = verticeB.split("-")
            if verticeB[0]=="T":
                busStationB = busStationB[1]
            else:
                busStationB = busStationB[0]
            barrio = getValueFast(map,busStationB)
            textote += f", Has llegado al barrio: {barrio}"
        textote+="\n"
    return textote,transbordo

def printeoQuinto(analyzer,resp,estacionOrigen):
    estacionOrigen = controller.formateo(estacionOrigen)
    imprimible = lt.newList("SINGLE_LINKED")
    graph = analyzer["DiGraph"]
    mapLatLog = analyzer["id->Coordenadas HASH"]
    paths = dj.Dijkstra(graph,estacionOrigen)
    for estacionDestino in lt.iterator(resp):
        if dj.hasPathTo(paths, estacionDestino):
            weightAllPath = str(dj.distTo(paths,estacionDestino))+"Km"
            try:
                tupla = getValueFast(mapLatLog,estacionDestino)
                tuplaLina = f"latitud:{str(tupla[0])}, longitud:{str(tupla[1])}"
            except:
                tuplaLina = "Error 404 - latitude and longitude not found"
            metible = [estacionDestino,tuplaLina,weightAllPath]
            lt.addLast(imprimible,metible)
    
        #! hora de hacer la tablita >:)
    table = ptbl()
    table.field_names = ["Nombre de la Estación + Bus Code", "Latitud y Longitud","Camino más corto para llegar desde el origen (dijkstra)"]
    for x in lt.iterator(imprimible):
        print(x[0])
        table.add_row(x)
    table.hrules = True
    return table





#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 1]  =^..^=    =^..^=    =^..^=    =^..^=

def buscarCaminoPosibleEntreDosEstaciones(graph, startStop, endStop):

    search = dfs.DepthFirstSearch(graph, startStop)

    if dfs.hasPathTo(search, endStop):
        stack = dfs.pathTo(search, endStop)
        totalStops = st.size(stack)
        totalTransbordos = 0
        path = lt.newList(cmpfunction=compareList)
        totalDistance = 0


        while not(st.isEmpty(stack)):
            stop = st.pop(stack)
            if stop[0] == "T":
                totalTransbordos += 1
                nextStop = st.top(stack)
                stop = stop + f"   -- Realiza transbordo a la ruta ({nextStop})"
                lt.addLast(path, stop)

            elif st.size(stack) > 0:
                nextStop = st.top(stack)
                if nextStop[0] == "T":
                    stop = stop + f" !! Parada en estación de transbordo ({nextStop})"
                    lt.addLast(path, stop)

                else:
                    edge = gr.getEdge(graph, stop, nextStop)
                    distance = edge['weight']
                    totalDistance += distance
                    stop = stop + f" -> Distancia a la siguiente parada ({nextStop}) : {round(distance, 2)} Km"
                    lt.addLast(path, stop)

            else:
                stop = stop + " < Destino"
                lt.addLast(path, stop)

        return round(totalDistance, 2), totalStops, totalTransbordos, path

    else:
        return None

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 2]  =^..^=    =^..^=    =^..^=    =^..^=

def buscarCaminoOptimoEntreDosEstaciones(analyzer, startStop, endStop):
    graph = analyzer["DiGraph"]
    search = bfs.BreadhtFisrtSearch(graph, startStop)

    if bfs.hasPathTo(search, endStop):
        stack = bfs.pathTo(search, endStop)
        totalStops = st.size(stack)
        return totalStops, stack
    else:
        print("No hay nada")

def distancias(analyzer,pathList):
    hashMap = analyzer["id->Coordenadas HASH"]
    distanciaTotal = 0
    pesosList = lt.newList("SINGLE_LINKED")
    txt=""
    newList = lt.newList("SINGLE_LINKED")
    for elemento in lt.iterator(pathList):
        if not(elemento[0]=="T"):
            lt.addLast(newList,elemento)
        # ACÁ SE LIMPIAN LOS DATOS (SE QUITAN LOS TRANSBORDOS)
    while (lt.size(newList))>1:
        uno = lt.firstElement(newList)
        txt += str(uno) + " --> "
        lt.removeFirst(newList)
        dos = lt.firstElement(newList)
        coorA = getValueFast(hashMap, uno)
        coorB = getValueFast(hashMap, dos)
        weight = haversine(coorA, coorB)
        txt += str(round(weight,2)) + "Km --> "
        distanciaTotal += weight
        lt.addLast(pesosList,weight)

    return distanciaTotal,txt

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 3]  =^..^=    =^..^=    =^..^=    =^..^=

def reconocerComponentesConectados(analyzer):
    graph = analyzer['DiGraph']
    search = scc.KosarajuSCC(graph)
    totalScc = scc.connectedComponents(search)
    listOfScc = organizeScc(search, totalScc)

    table = tableScc(listOfScc)
    
    return totalScc, table


#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 4]  =^..^=    =^..^=    =^..^=    =^..^=

def requerimientoCuatro(analyzer,localizacionOrigen,localizacionDestino):
    hashMap = analyzer["id->Coordenadas HASH"]
    graph = analyzer["DiGraph"]
    distanciaMinimaOrigen,listEstacionesOrigen = estacionMasCercana(hashMap,localizacionOrigen)
    distanciaMinimaDestino,listEstacionesDestino = estacionMasCercana(hashMap,localizacionDestino)
        #!PRUEBA
    # for x in lt.iterator(listEstacionesOrigen):
    #     print(x)
    # print(distanciaMinimaOrigen)
    # print("="*15)
    # for x in lt.iterator(listEstacionesDestino):
    #     print(x)
    # print(distanciaMinimaDestino)
        #! YA ENCUENTRA LA ESTACIÓN MÁS CERCANA
    rbtStacksPerWeight = om.newMap("RBT",compareList)
    for estacionOrigen in lt.iterator(listEstacionesOrigen):
        paths = dj.Dijkstra(graph,estacionOrigen)
        for estacionDestino in lt.iterator(listEstacionesDestino):
            if dj.hasPathTo(paths, estacionDestino):
                stack = dj.pathTo(paths, estacionDestino)
                weightAllPath = dj.distTo(paths,estacionDestino)
                if not(mp.contains(rbtStacksPerWeight,weightAllPath)):
                    mp.put(rbtStacksPerWeight,weightAllPath,stack)
    
    # ya tenemos un RBT ordenado por el peso de los caminos

    pesoMinimo = om.minKey(rbtStacksPerWeight)
    llaveValor = om.get(rbtStacksPerWeight,pesoMinimo)
    stackMenor = me.getValue(llaveValor)

    return distanciaMinimaOrigen,distanciaMinimaDestino,pesoMinimo,stackMenor

def estacionMasCercana (hashMap,location):
    keyList = mp.keySet(hashMap)
    arbolitoRBT = om.newMap("RBT",compareList)
    for key in lt.iterator(keyList):
        tupla = getValueFast(hashMap,key)
        tupla = (float(tupla[0]),float(tupla[1]))
        distancia = haversine(tupla,location)

            #ACÁ METEMOS EN EL RBT COMO LLAVE LA DISTANCIA (PARA LUEGO SACAR LA MENOR)
            #Y COMO VALOR EL NOMBRE DEL NODO EN EL GRÁFO, PARA SACARLO LUEGO
        if not(om.contains(arbolitoRBT,distancia)):
            listitaDeNodos = lt.newList("SINGLE_LINKED",compareList)
            om.put(arbolitoRBT,distancia,listitaDeNodos)
        llaveValor = om.get(arbolitoRBT,distancia)
        listitaDeNodosALlenar = me.getValue(llaveValor)
        lt.addLast(listitaDeNodosALlenar,key)
    distanciaMinima = om.minKey(arbolitoRBT)
    llaveValor = om.get(arbolitoRBT,distanciaMinima)
    listResp = me.getValue(llaveValor)
    return distanciaMinima,listResp
    


#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 5]  =^..^=    =^..^=    =^..^=    =^..^=

def reqCinco(analyzer,estacionOrigen,count):
    graph = analyzer["DiGraph"]
    adyacentListOG = gr.adjacents(graph,estacionOrigen)
    metida = lt.newList("SINGLE_LINKED")

    #!  SÉ QUE ESTOY COMETIENDO UN CRIMEN DE GUERRA CON LO QUE ESTOY HACIENDO
    #!  PERO JURO HABER INTENTADO TODO TIPO DE COPY, DEEPCOPY O  LIBRERIA EXTERNA
    
    i=0
    while count>i:
        for adyacente in lt.iterator(adyacentListOG):
            adyacentListChange = gr.adjacents(graph,adyacente)
            for metible in lt.iterator(adyacentListChange):
                if not(lt.isPresent(adyacentListOG, metible)):
                    lt.addLast(metida,metible)
        for elemento in lt.iterator(metida):
            if not(lt.isPresent(adyacentListOG,elemento)) and elemento!=estacionOrigen:
                lt.addLast(adyacentListOG,elemento)
        i+=1
    return(adyacentListOG,lt.size(adyacentListOG))
#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 6]  =^..^=    =^..^=    =^..^=    =^..^=
def requerimientoSix(analyzer,estacionOrigen,neighborhoodDestino):
    map = analyzer["hashPerNeighborhood"]
    graph = analyzer["DiGraph"]
    listOfPossibleEndStations = getValueFast(map,neighborhoodDestino)

    paths = dj.Dijkstra(graph,estacionOrigen)
    rbtStacksPerWeight = om.newMap("RBT",compareList)
    for endStation in lt.iterator(listOfPossibleEndStations):
        if dj.hasPathTo(paths, endStation):
            stack = dj.pathTo(paths, endStation)
            weightAllPath = dj.distTo(paths,endStation)
            if not(mp.contains(rbtStacksPerWeight,weightAllPath)):
                mp.put(rbtStacksPerWeight,weightAllPath,stack)
    pesoMinimo = om.minKey(rbtStacksPerWeight)
    llaveValor = om.get(rbtStacksPerWeight,pesoMinimo)
    stackMenor = me.getValue(llaveValor)
    size = st.size(stackMenor)

    return pesoMinimo,stackMenor,size

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 7]  =^..^=    =^..^=    =^..^=    =^..^=

def findCirclePath(origin, analyzer):
    diGraph = analyzer['DiGraph']
    listaLlegan = lt.newList("SINGLE_LINKED")
    for vertice in lt.iterator(gr.vertices(diGraph)):
        for adyacente in lt.iterator((gr.adjacents(diGraph,vertice))):
            if adyacente == origin:
                lt.addLast(listaLlegan,vertice)    
    rbtStacksPerWeight = om.newMap("RBT",compareList)
    search = dfs.DepthFirstSearch(diGraph, origin)
    for destino in lt.iterator(listaLlegan):
        stack = dfs.pathTo(search,destino)
        size = (st.size(stack))
        if size>2:
            if not(mp.contains(rbtStacksPerWeight,size)):
                mp.put(rbtStacksPerWeight,size,stack)
    try:
        caminosMinimos = om.minKey(rbtStacksPerWeight)
    except:
        print("Hey, ¡me temo que no hay caminos circulares para esta ubicación, intenta con otro vertice!")
        sys.exit(0)
    llaveValor = om.get(rbtStacksPerWeight,caminosMinimos)
    stackMenor = me.getValue(llaveValor)
    return caminosMinimos, stackMenor

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 8]  =^..^=    =^..^=    =^..^=    =^..^=



#! =^..^=   =^..^=   =^..^=    =^..^=  [Funciones utilizadas para comparar elementos]  =^..^=    =^..^=    =^..^=    =^..^=

def compareStopIds(stop, keyvaluestop):
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1
    
def compareMapID(id, entry):
    idEntry = me.getKey(entry)
    if (id == idEntry):
        return 0
    elif (id > idEntry):
        return 1
    else:
        return -1
    
def compareList(ruta1, ruta2):
    if (ruta1 == ruta2):
        return 0
    elif (ruta1 > ruta2):
        return 1
    else:
        return -1
    
def cmpRutas(ruta1, ruta2):
    if (ruta1 == ruta2):
        return True
    elif (ruta1 > ruta2):
        return False
    else:
        return True

def cmpByListSize(list1, list2):
    if (lt.size(list1) == lt.size(list2)):
        return True
    elif (lt.size(list1) < lt.size(list2)):
        return False
    else:
        return True


# Funciones de ordenamiento
    

#Funciones útiles
    
def getValueFast(map, key):

    entry = mp.get(map, key)

    value = me.getValue(entry)

    return value
    
def printVerteces(graph, analyzer):
    graph = analyzer[graph]
    list = gr.vertices(graph)
    for vertex in lt.iterator(list):
        print(vertex)

def printEdges(graph, analyzer):
    graph = analyzer[graph]
    list = gr.edges(graph)
    for edge in lt.iterator(list):
        print(edge)

def countRutas(analyzer):
    

    rutasList = ms.sort(analyzer["rutas LIST"], cmpRutas)
    
    uniques = 1
    last = lt.firstElement(rutasList)
    for ruta in lt.iterator(rutasList):
        if last != ruta:
            uniques += 1
            last = ruta

    return uniques

def rangoArea(analyzer):
    longMin = om.minKey(analyzer["mapa de longitudes"])
    longMax = om.maxKey(analyzer["mapa de longitudes"])

    latMin = om.minKey(analyzer["mapa de latitudes"])
    latMax = om.maxKey(analyzer["mapa de latitudes"])

    area = (longMax-longMin) * (latMax-latMin)

    return area, longMin, longMax,  latMin, latMax

def firstAndLast5(graph, analyzer):
    firstAndLast5LIST = lt.newList(cmpfunction=compareStopIds)
    vertexLIST = gr.vertices(graph)

    for vertex in lt.iterator(vertexLIST):
        if vertex[0] != "T":
            identificador = vertex
            coor = getValueFast(analyzer["id->Coordenadas HASH"], identificador)
            edgesLIST = gr.adjacentEdges(graph, vertex)
            adj = 0
            for edge in lt.iterator(edgesLIST):
                if edge["weight"] != 0:
                    adj += 1

            element = {"identificador": identificador, "geo": coor, "adj": adj//2}
            lt.addLast(firstAndLast5LIST, element)
        
    table = cargaDeDatosVISUAL(firstAndLast5LIST)

    return table


def printkeys(analyzer):
    keys = mp.keySet(analyzer["id->Coordenadas HASH"])

    for k in lt.iterator(keys):
        print(k)


def organizeScc(search, totalScc):
    #Crea una lista de listas organizada para poder sacar del hash lo que sirve
    hash = search['idscc']
    keys = mp.keySet(hash)
    output= lt.newList(cmpfunction = compareList)

    for i in range(0, totalScc):
        newList = lt.newList(cmpfunction=compareList)
        lt.addLast(output, newList)

    for stop in lt.iterator(keys):
        pos = getValueFast(hash, stop)
        list = lt.getElement(output, pos)
        lt.addLast(list, stop)

    for scc in lt.iterator(output):
        ms.sort(scc, cmpRutas)
    
    ms.sort(output, cmpByListSize)

    return output

def tableScc(listOfScc):
    table = ptbl()
    table.field_names = ["Número de estaciones", "Estaciones (tres primeras y tres últimas)"]
    table.align["Estaciones (tres primeras y tres últimas)"] = "l"


    i = 1
    while i <= 5:
        scc = lt.getElement(listOfScc, i)
        row = []
        numStops = lt.size(scc)
        row.append(numStops)
        stopsScc = printStopsScc(scc)
        row.append(stopsScc)
        table.add_row(row)
        table.hrules = True
        i+=1

    return table


def printStopsScc(scc):
    if lt.size(scc) <= 6:
        output = ""
        for stop in lt.iterator(scc):
            output = output + f" - {stop}\n"
    else:
        output = ""
        
        for i in range(1, 4):
            stop = lt.getElement(scc, i)
            output = output + f" - {stop}\n"

        output = output + "...\n"

        for j in range(0, 3):
            stop = lt.getElement(scc, lt.size(scc) - j)
            output = output + f" - {stop}\n"

    return output

#PARA IMPRIMIR TABLAS Y COSAS

def tableDiGraph(analyzer):
    graph = analyzer["DiGraph"]
    verteces = gr.vertices(graph)
    ms.sort(verteces, cmpRutas)

    table = ptbl()
    table.field_names = ["Node_ID", "Code", "Bus_Stop", "Transport", "Longitude", "Latitude", "District_Name", "Neighborhood_Name", "In Degree (Routes)", "Out Degree (Routes)"]
    listSize = lt.size(verteces)

    i = 1
    while i <= 5:

        stop = lt.getElement(verteces, i)
        row = []
        row.append(stop)

        if stop[0] == "T":
            code = stop[2:]
            busStop = "T-BUS"
            transport = "Transfer bus"
        else:
            code = stop[0:5]
            busStop = "BUS-" + stop[5:]
            transport = "Day bus stop"

        row.append(code)
        row.append(busStop)
        row.append(transport)

        latitude, longitude = getValueFast(analyzer["id->Coordenadas HASH"], stop)
        
        row.append(longitude)
        row.append(latitude)

        disctrict = getValueFast(analyzer["id->District_Name HASH"], stop)
        row.append(disctrict)   

        neighbor = getValueFast(analyzer["id->Neighborhood_Name HASH"], stop) 
        row.append(neighbor)

        indegree = gr.indegree(graph, stop)
        row.append(indegree)

        outdegree = gr.outdegree(graph, stop)
        row.append(outdegree)

        table.add_row(row)
        table.hrules = True

        i +=1

    j = listSize - 4
    while j <= listSize:

        stop = lt.getElement(verteces, j)

        row = []
        row.append(stop)

        if stop[0] == "T":
            code = stop[2:]
            busStop = "T-BUS"
            transport = "Transfer bus"
        else:
            code = stop[0:5]
            busStop = "BUS-" + stop[5:]
            transport = "Day bus stop"

        row.append(code)
        row.append(busStop)
        row.append(transport)
        print(stop)

        latitude, longitude = getValueFast(analyzer["id->Coordenadas HASH"], stop)
        
        row.append(longitude)
        row.append(latitude)

        disctrict = getValueFast(analyzer["id->District_Name HASH"], stop)
        row.append(disctrict)   

        neighbor = getValueFast(analyzer["id->Neighborhood_Name HASH"], stop) 
        row.append(neighbor)

        indegree = gr.indegree(graph, stop)
        row.append(indegree)

        outdegree = gr.outdegree(graph, stop)
        row.append(outdegree)

        table.add_row(row)
        table.hrules = True

        j += 1


    return table

def tableGraph(analyzer):
    graph = analyzer["graph"]
    verteces = gr.vertices(graph)
    ms.sort(verteces, cmpRutas)

    table = ptbl()
    table.field_names = ["Node_ID", "Code", "Bus_Stop", "Transport", "Longitude", "Latitude", "District_Name", "Neighborhood_Name", "Degree (Rep Routes)"]
    listSize = lt.size(verteces)

    i = 1
    while i <= 5:

        stop = lt.getElement(verteces, i)
        row = []
        row.append(stop)

        if stop[0] == "T":
            code = stop[2:]
            busStop = "T-BUS"
            transport = "Transfer bus"
        else:
            code = stop[0:5]
            busStop = "BUS-" + stop[5:]
            transport = "Day bus stop"

        row.append(code)
        row.append(busStop)
        row.append(transport)

        latitude, longitude = getValueFast(analyzer["id->Coordenadas HASH"], stop)
        
        row.append(longitude)
        row.append(latitude)

        disctrict = getValueFast(analyzer["id->District_Name HASH"], stop)
        row.append(disctrict)   

        neighbor = getValueFast(analyzer["id->Neighborhood_Name HASH"], stop) 
        row.append(neighbor)

        degree = gr.degree(graph, stop)//2
        row.append(degree)

        table.add_row(row)
        table.hrules = True

        i +=1

    j = listSize - 4
    while j <= listSize:

        stop = lt.getElement(verteces, j)

        row = []
        row.append(stop)

        if stop[0] == "T":
            code = stop[2:]
            busStop = "T-BUS"
            transport = "Transfer bus"
        else:
            code = stop[0:5]
            busStop = "BUS-" + stop[5:]
            transport = "Day bus stop"

        row.append(code)
        row.append(busStop)
        row.append(transport)
        print(stop)

        latitude, longitude = getValueFast(analyzer["id->Coordenadas HASH"], stop)
        
        row.append(longitude)
        row.append(latitude)

        disctrict = getValueFast(analyzer["id->District_Name HASH"], stop)
        row.append(disctrict)   

        neighbor = getValueFast(analyzer["id->Neighborhood_Name HASH"], stop) 
        row.append(neighbor)

        degree = gr.degree(graph, stop)//2
        row.append(degree)

        table.add_row(row)
        table.hrules = True

        j += 1


    return table

def cargaDeDatosVISUAL(list):
    table = ptbl()
    table.field_names = ["Identificador de la estación (Code-Ruta)", "Geolocalización (Latitud, Longitud)", "Número de estaciones de conexión"]
    listSize = lt.size(list)

    i = 1
    while i <= 5:

        stop = lt.getElement(list, i)
        row = []
        row.append(stop["identificador"])
        row.append(stop["geo"])
        row.append(stop["adj"])

        table.add_row(row)
        table.hrules = True

        i += 1

    j = listSize - 4
  
    while j <= listSize:

        stop = lt.getElement(list, j)
        row = []
        row.append(stop["identificador"])
        row.append(stop["geo"])
        row.append(stop["adj"])

        table.add_row(row)
        table.hrules = True

        j += 1


    return table

def countExclusive(analyzer, exclusiveBusStopsRoutes):
    graph = analyzer["graph"]
    verteces = gr.vertices(graph)
    edges = gr.edges(graph)

    totalBusStops = lt.size(verteces)
    

    sharedBusStops = 0
    sharedBusRoutes = 0



    for vertex in lt.iterator(verteces):
        if vertex[0] == "T":
            sharedBusStops += 1
            sharedBusRoutes += gr.degree(graph, vertex)


    exclusiveBusStops = totalBusStops - sharedBusStops
    totalBusStopsRoutes = exclusiveBusStopsRoutes + sharedBusRoutes

    return totalBusStops, exclusiveBusStops, sharedBusStops, totalBusStopsRoutes, exclusiveBusStopsRoutes, sharedBusRoutes

def graphSpecs(analyzer, graph):
    graph = analyzer[graph]
    nodes = gr.numVertices(graph)
    if graph == "graph":
        edges = gr.numEdges(graph)//2
    else:
        edges = gr.numEdges(graph)

    return nodes, edges

