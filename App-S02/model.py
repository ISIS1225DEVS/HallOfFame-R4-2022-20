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
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT import graph as gr
from DISClib.Utils import error as error
from DISClib.ADT import orderedmap as om
from DISClib.ADT import stack as st
from DISClib.ADT import queue
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import bellmanford as bfa
from DISClib.Algorithms.Graphs import bfs as bfs
from DISClib.Algorithms.Graphs import dfs
from math import radians, cos, sin, asin, sqrt
assert cf
import numpy as np

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos
def newAnalyzer():
    analyzer = {
        'stopMap': None,
        'stops': None,
    }
    analyzer['stops'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)
    analyzer['stopMap'] = mp.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareEdgesIds)
    analyzer['paradas'] = mp.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareEdgesIds)
    
    analyzer['latitude'] = om.newMap(omaptype="RBT",
                                      comparefunction=compareLat)
    
    analyzer['longitude'] = om.newMap(omaptype="RBT",
                                      comparefunction=compareLat)
    analyzer['stopVertex'] = lt.newList('ARRAY_LIST')

    analyzer['Bus_routes'] = mp.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareEdgesIds)
    
    return analyzer
# Funciones para agregar informacion al catalogo

def addStop(analyzer, stop): #agrega información de las paradas a un mapa y si es trasbordo lo hace como una lista de las rutas de buses
    entry = mp.get(analyzer['stopMap'], stop['ID'])
    if entry is None:
        mp.put(analyzer['stopMap'], stop['ID'], stop)
    return analyzer

def addStopVertex(analyzer, stop): #agrega un vertice por estación
    id = str(stop['ID'])
    #print(not gr.containsVertex(analyzer['stops'], id))
    if not gr.containsVertex(analyzer['stops'], id):
        #print('Damn Bitch')
        gr.insertVertex(analyzer['stops'], id)
    return analyzer 

def addLatitude(analyzer, stop):
    key = stop['Latitude']
    entry = om.get(analyzer['latitude'], key)
    #print(entry is None)
    if entry is None:
        #print('Damn Bitch')
        om.put(analyzer['latitude'], key, stop)
    return analyzer

def addLongitude(analyzer, stop):
    key = stop['Longitude']
    entry = om.get(analyzer['longitude'], key)
    #print(entry is None)
    if entry is None:
        #print('Damn Bitch')
        om.put(analyzer['longitude'], key, stop)
    return analyzer

def addRoute(analyzer, stop):
    key = stop['Bus_Stop']
    entry = mp.get(analyzer['Bus_routes'], key)
    #print(entry is None)
    if entry is None:
        #print('Damn Bitch')
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, stop)
        mp.put(analyzer['Bus_routes'], key, lstroutes)
    else:
        lstroutes = me.getValue(entry)
        info = stop
        lt.addLast(lstroutes, info)
        mp.put(analyzer['Bus_routes'], key, lstroutes)
    return analyzer


def addConnection(analyzer, edge): #agrega los arcos entre las estaciones
    origin = str(formatOrigin(edge))
    destination = str(formatDesti(edge))
    if gr.containsVertex(analyzer['stops'], origin) and gr.containsVertex(analyzer['stops'], destination):
        edge = gr.getEdge(analyzer['stops'], origin, destination)
        if edge is None:
            distance = haversine(analyzer, origin, destination)
            gr.addEdge(analyzer['stops'], origin, destination, distance)
            gr.addEdge(analyzer['stops'], destination, origin, distance)
    return analyzer

def addRouteToEstation(analyzer, stop):
    addRouteStop(analyzer, stop)
    addRouteConnections(analyzer)
    return analyzer

def addRouteStop(analyzer, stop):
    entry = mp.get(analyzer['paradas'], stop['Code'])
    #print(entry is None)
    if entry is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, stop['ID'])
        key = "T-" + str(stop['Code'])
        mp.put(analyzer['paradas'], key, lstroutes)
        mp.put(analyzer['stopMap'], key, stop)
    else:
        lstroutes = entry['value']
        info = stop['ID']
        if not lt.isPresent(lstroutes, info):
            lt.addLast(lstroutes, info)
        mp.put(analyzer['stopMap'], key, stop)
    return analyzer

def addRouteConnections(analyzer):
    lststops = mp.keySet(analyzer['paradas'])
    for key in lt.iterator(lststops):
        if not gr.containsVertex(analyzer['stops'], key):
            gr.insertVertex(analyzer['stops'], key)
        lstroutes = mp.get(analyzer['paradas'], key)['value']
        #prevrout = None
        for route in lt.iterator(lstroutes):
            #if prevrout is not None:
            addConnectionTransbordo(analyzer, key, route, 0)
            addConnectionTransbordo(analyzer, route, key, 0)
            #prevrout = route

def addConnectionTransbordo(analyzer, prevrout, route, distance):
    if gr.containsVertex(analyzer['stops'], prevrout) and gr.containsVertex(analyzer['stops'], route):
        edge = gr.getEdge(analyzer['stops'], prevrout, route)
        if edge is None:
            gr.addEdge(analyzer['stops'], prevrout, route, distance)
    return analyzer
    
       
def formatOrigin(edge):
    bus_stop = (edge['Bus_Stop'].split("-"))[1].strip()
    name = edge['Code'] + "-" + bus_stop
    return name 
def formatDesti(edge):
    bus_stop = (edge['Bus_Stop'].split("-"))[1].strip()
    name = edge['Code_Destiny'] + "-" + bus_stop
    return name 

# Funciones para creacion de datos

#Funciones Req1
def req1(origen, destino, analyzer):
    print(origen,destino)
    #grafo  = djk.Dijkstra(analyzer['stops'], origen)
    #existe = djk.hasPathTo(grafo, destino)
    grafo  = bfa.BellmanFord(analyzer['stops'], origen)
    existe = bfa.hasPathTo(grafo, destino)
    dic = {}
    cont = 0
    if existe:
        costo = 0
        #dic['camino'] = djk.pathTo(grafo, destino)
        dic['camino'] = bfa.pathTo(grafo, destino)
        dic['tamano'] = st.size(dic['camino'])
        for i in lt.iterator(dic['camino']):
            info = me.getValue(mp.get(analyzer['stopMap'], i['vertexA']))
            if info['Transbordo'] == "S":
            #if "T" in i['vertexA']:
                cont += 1
            costo += i['weight']
        dic['transbordo'] = cont
        dic['costo'] = costo
    return existe, dic

#Funciones Req2
def req2(origen, destino, analyzer):
    print(origen,destino)
    grafo  = djk.Dijkstra(analyzer['stops'], origen)
    existe = djk.hasPathTo(grafo, destino)
    #grafo  = bfa.BellmanFord(analyzer['stops'], origen)
    #existe = bfa.hasPathTo(grafo, destino)
    dic = {}
    cont = 0
    if existe:
        costo = 0
        dic['camino'] = djk.pathTo(grafo, destino)
        #dic['camino'] = bfa.pathTo(grafo, destino)
        dic['tamano'] = st.size(dic['camino'])
        for i in lt.iterator(dic['camino']):
            info = me.getValue(mp.get(analyzer['stopMap'], i['vertexA']))
            if info['Transbordo'] == "S":
            #if "T" in i['vertexA']:
                cont += 1
            costo += i['weight']
        dic['transbordo'] = cont
        dic['costo'] = costo
    return existe, dic

#Funciones Req4
def req4(origen, destino, dist, analyzer):
    origen = origen['Code']
    destino = destino['Code']
    lststops = mp.keySet(analyzer['stopMap'])
    for key in lt.iterator(lststops):
        parada = key.split('-')[0]
        if parada==origen:
            origen = key
        if parada==destino:
            destino = key
    grafo  = djk.Dijkstra(analyzer['stops'], origen)
    existe = djk.hasPathTo(grafo, destino)
    #print(origen,destino,existe)
    dic = {'origen':origen,'destino':destino,'d_org':dist[0],'d_des':dist[1]}
    cont = 0
    if existe:
        costo = 0
        dic['camino'] = djk.pathTo(grafo, destino)
        dic['tamano'] = st.size(dic['camino'])
        for i in lt.iterator(dic['camino']):
            #print(i)
            if 'T-' in i['vertexA']:
                cont += 1
            costo += i['weight']
        dic['transbordo'] = cont
        dic['costo'] = costo
    else:
        print('No hay camino para llegar de la estación {} (la más cercana al origen y {} (la más cercana al destino).'.format(origen,destino))
    return existe,dic

def closest_est(origen, destino, analyzer):
    dist_org = np.inf
    dist_des = np.inf
    org = {}
    des = {}
    for parada in lt.iterator(analyzer['stopVertex']):
        d1 = calc_harvesine(origen,parada)
        d2 = calc_harvesine(destino,parada)
        if d1<dist_org:
            org = parada
            dist_org = d1
        if d2<dist_des:
            des = parada
            dist_des = d2
    return org,des,dist_org,dist_des

#Funciones Req5
def req5(origen,n,analyzer):
    existe = gr.containsVertex(analyzer['stops'], origen)
    if existe:
        #recorrido_bfs = bfs.BreadhtFisrtSearch(analyzer['stops'],origen)
        #print(recorrido_bfs)
        #print(set(lt.iterator(gr.adjacents(analyzer['stops'],origen))))
        #print(gr.adjacentEdges(analyzer['stops'],origen))
        estaciones = bfs_mod([origen],set(),n,0,analyzer)
        lststops = mp.keySet(analyzer['stopMap'])
        grafo  = djk.Dijkstra(analyzer['stops'], origen)
        data = []
        for estacion in estaciones:
            for key in lt.iterator(lststops):
                parada = key.split('-')[0]
                if parada == estacion:
                    cont = 0
                    costo = 0
                    saltos = 0
                    dic = {'destino':parada}
                    dic['camino'] = djk.pathTo(grafo, key)
                    dic['tamano'] = st.size(dic['camino'])
                    for i in lt.iterator(dic['camino']):
                        #print(i)
                        if 'T-' in i['vertexA']:
                            cont += 1
                        if i['weight'] != 0:
                            saltos += 1
                        costo += i['weight']
                    dic['saltos'] = saltos
                    info = me.getValue(mp.get(analyzer['stopMap'], key))
                    dic['info'] = info
                    dic['transbordo'] = cont
                    dic['costo'] = costo
                    data+=[dic]
                    break
        return data
    else:
        print('Introduzca un vertice en el grafo')


def req7(analyzer, origen):
    camino = []
    camino = dfs_mod(set(), analyzer, origen,camino, 1, 0)
    for esta in camino:
        #print(esta)
        inicio = esta['vertexB']
        final = esta['vertexA']
        arco = gr.getEdge(analyzer['stops'], inicio, final)
        camino = camino + [arco]
    return camino

def bfs_mod(list_origen,e_visitadas,n,m,analyzer):
    if m<=n:
        to_visit = set()
        for origen in list_origen:
            for i in lt.iterator(gr.adjacents(analyzer['stops'],origen)):
                if sacar_estacion(i) not in e_visitadas:
                    if 'T-' in i:
                        to_visit = to_visit.union(set(lt.iterator(gr.adjacents(analyzer['stops'],i))))
                    else:
                        to_visit = to_visit.union({i})    
            e_visitadas = e_visitadas.union({sacar_estacion(origen)})
        m+=1
        list_origen = list(to_visit)
        return bfs_mod(list_origen,e_visitadas,n,m,analyzer)
    else:
        return e_visitadas

def dfs_mod(e_visitadas, analyzer, origen, camino, n, m):
    to_visit = set()
    if m<= n:
        no_pasa = True
        for k in lt.iterator(gr.adjacentEdges(analyzer['stops'],origen)):
            i = k['vertexB']
            if sacar_estacion(i) not in e_visitadas:
                no_pasa = False
                if 'T-' in i:
                    to_visit = to_visit.union(set(lt.iterator(gr.adjacents(analyzer['stops'],i))))
                    e_visitadas = e_visitadas.union({sacar_estacion(i)}) 
                    for j in to_visit:
                        camino1 = camino +[k]
                        return dfs_mod(e_visitadas, analyzer, j, camino1, n, m)
                else:
                    camino1 = camino + [k]
                    return dfs_mod(e_visitadas, analyzer, i, camino1, n, (m+1))
        if no_pasa:
            return camino
    else:
        return camino


    

def sacar_estacion(cosa):
    if 'T-' in cosa:
        return cosa.replace('T-','')
    else:
        return cosa.split('-')[0]    

#Funciones req6
def req6(origen,vecindario_destino,analyzer):
    existe = gr.containsVertex(analyzer['stops'], origen)
    if existe:
        no_encontro = True
        est_barrio = []
        for key in lt.iterator(analyzer['stopVertex']):
            if key['Neighborhood_Name']==vecindario_destino:
                est_barrio.append(key['ID'])
        if len(est_barrio)!=0:
            no_encontro = False
        if no_encontro:
            print('Introduzca un nombre de barrio válido')
        else:
            grafo  = djk.Dijkstra(analyzer['stops'], origen)
            longitud = np.infty
            camino = {}
            for destino in est_barrio:
                existe1 = djk.hasPathTo(grafo, destino)
                if existe1:
                    camino1 = djk.pathTo(grafo, destino)
                    costo = 0
                    for i in lt.iterator(camino1):
                        costo += i['weight']
                    if costo<longitud:
                        camino = camino1
                        longitud = costo
            if camino == {}:
                print('No hay camino desde origen al barrio propuesto') 
            else:
                cont = 0
                dic = {'origen':origen,'destino':destino}
                dic['camino'] = camino
                dic['tamano'] = st.size(dic['camino'])
                for i in lt.iterator(dic['camino']):
                    #print(i)
                    if 'T-' in i['vertexA']:
                        cont += 1
                dic['transbordo'] = cont
                dic['costo'] = costo
                return dic
    else:
        print('Introduzca un vertice en el grafo')



# Funciones de consulta


def getStopFromList(analyzer, stop):
    value = me.getValue(mp.get(analyzer['stopMap'], stop))
    return value

def haversine(analyzer, origin, destination): 
    origen = getStopFromList(analyzer, origin)
    destiny = getStopFromList(analyzer, destination)
    return calc_harvesine(origen,destiny)

def calc_harvesine(origen,destiny):
    distance = 0
    lat1 = radians(float(origen['Latitude']))
    lat2 = radians(float(destiny['Latitude']))
    lon1 = float(origen['Longitude'])
    lon2 = float(origen['Longitude'])
    dLat = radians(lat2- lat1)
    dlon = radians(lon2 - lon1)
    R = 6372.8 #Esta en Km y es el radio de la tierra
    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    distance = R * c
    return distance

def getTotalRoutes(analyzer): #da el total de rutas que se cargaron
    return mp.size(analyzer['Bus_routes'])

def getTotalRoutesExclus(analyzer): #da el total de rutas que se cargaron
    return mp.size(analyzer['stopMap'])

def getTotalTransbordo(analyzer):
    return mp.size(analyzer['paradas'])

def getEdges(analyzer):
    return gr.numEdges(analyzer['stops'])

def getMinlon(analyzer):
    return om.minKey(analyzer['longitude'])

def getMinlat(analyzer):
    return om.minKey(analyzer['latitude'])

def getMaxlon(analyzer):
    return om.maxKey(analyzer['longitude'])

def getMaxlat(analyzer):
    return om.maxKey(analyzer['latitude'])

def getVertex(analyzer):
    return gr.vertices(analyzer['stops'])

def getInfoLoad(analyzer, stop): 
    lst = analyzer['stopVertex']
    lt.addLast(lst, stop)
    return lst

def getFirstLast(lst, analyzer): #recibe la lista de vertices y busca los 5 primeros y 5 ultimos para extraer su info.
    i = 0
    lista = lt.newList()
    for stop in lt.iterator(lst):
        adjacent = lt.size(gr.adjacents(analyzer['stops'], stop['ID']))
        stop['adjacent'] = adjacent
        if i<= 4 or i >= lt.size(lst) - 5:
            lt.addLast(lista, stop)
        i += 1
    return lista
    




# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento

#Funciones de Comparación
def compareEdgesIds(stop, keyvaluestop):
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1

def compareStopIds(stop, keyvaluestop):
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1

def compareroutes(route1, route2):
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

def compareLat(date1, date2):
    if (date1 == date2):
        return 0
    elif (date1 > date2):
        return 1
    else:
        return -1