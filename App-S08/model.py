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


import math
import config as cf

from DISClib.ADT import stack as st
from DISClib.ADT import graph as gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp

from DISClib.Algorithms.Graphs import scc
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Sorting import shellsort as shs
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import scc
from DISClib.ADT import graph as gr
import time

assert cf

from tabulate import tabulate

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def initCatalog():
    catalog = {
        "gr_stations": gr.newGraph(datastructure='ADJ_LIST', directed=True, size=14000),
        "digr_stops": gr.newGraph(datastructure='ADJ_LIST', directed=True, size=14000),
        "mp_stations": mp.newMap(numelements=14000, maptype='PROBING'),
        "mp_nh": mp.newMap(numelements=14000, maptype='PROBING'),
        "lt_stops": lt.newList("ARRAY_LIST"),
        "lt_edges": lt.newList("ARRAY_LIST"),
        "lt_vertices": lt.newList("ARRAY_LIST")
    }

    return catalog

# Funciones para agregar informacion al catalogo

def addLtStops(catalog, stop):
    lt.addLast(catalog["lt_stops"], stop)

def addLtEdges(catalog, edge):
    lt.addLast(catalog["lt_edges"], edge)

def addMapStations(catalog):
    mp_stations = catalog["mp_stations"]
    lt_stops = catalog["lt_stops"]

    # recorre cada parada
    for stop in lt.iterator(lt_stops):
        # crea el codigo de ruta y lo agrega al map
        station = stop["Code"]
        bus = stop["Bus_Stop"].replace(" ", "").split("-")[1]
        transbordo = "T-" + station
        code_ruta = station + "-" + bus

        mp.put(mp_stations, code_ruta, stop)

        # si la estacion es tranbordo y no esta en el mapa, se crea en el mapa
        if stop["Transbordo"] == "S" and not mp.contains(mp_stations, transbordo):
            stop = stop.copy()
            stop["Bus_Stop" ] = "T-BUS"
            stop["Transport"] = "Transfer Bus"
            mp.put(mp_stations, transbordo, stop)

def addMapNH(catalog):
    mp_nh = catalog["mp_nh"]
    lt_stops = catalog["lt_stops"]

    for stop in lt.iterator(lt_stops):
        nh = stop["Neighborhood_Name"]
        if not mp.contains(mp_nh, nh):
            mp.put(mp_nh, nh, lt.newList("ARRAY_LIST"))

        lt_nh = me.getValue(mp.get(mp_nh, nh))
        lt.addLast(lt_nh, stop)

def addStops(catalog):
    lt_stops = catalog["lt_stops"]
    gr_stations = catalog["gr_stations"]
    digr_stops = catalog["digr_stops"]
    lt_add = catalog["lt_vertices"]
    lt_transfer= lt.newList("ARRAY_LIST")

    # recorre cada parada
    for stop in lt.iterator(lt_stops):
        station = stop["Code"]
        bus = stop["Bus_Stop"].replace(" ", "").split("-")[1]
        code_ruta = station + "-" + bus
        # crea el codigo de parada y lo agrega al grafo
        gr.insertVertex(gr_stations, code_ruta)
        gr.insertVertex(digr_stops, code_ruta)
        # se agrega a la lista de vertices
        lt.addLast(lt_add, code_ruta)

        # si es tranbordo se crea su codigo y se agrega a la lista de transbordos
        if stop["Transbordo"] == "S":
            transbordo = "T-" + station
            lt.addLast(lt_transfer, [transbordo, code_ruta])

    # se llama a la funcion para crear los transbordos
    addTransfer(catalog, lt_transfer)

def addTransfer(catalog, lt_transfer):
    gr_stations = catalog["gr_stations"]
    digr_stops = catalog["digr_stops"]
    lt_add = catalog["lt_vertices"]

    # recorre cada transbordo
    for tranfer in lt.iterator(lt_transfer):
        transbordo, code_ruta = tranfer[0], tranfer[1]
        # si no existe el vertice de transbordo lo agrega al grafo
        if not gr.containsVertex(gr_stations, transbordo):
                gr.insertVertex(gr_stations, transbordo)
                gr.insertVertex(digr_stops, transbordo)
                # agrega el codigo de vertice a la lista de vertices
                lt.addLast(lt_add, transbordo)
        # crea los arcos de ida y vuelta de la estacion del bus a la estacion tranbordo
        gr.addEdge(gr_stations, code_ruta, transbordo)
        gr.addEdge(gr_stations, transbordo, code_ruta)

        gr.addEdge(digr_stops, code_ruta, transbordo)
        gr.addEdge(digr_stops, transbordo, code_ruta)

def addEdges(catalog):
    lt_edges = catalog["lt_edges"]
    gr_stations = catalog["gr_stations"]
    digr_stops = catalog["digr_stops"]
    mp_stations = catalog["mp_stations"]

    # recorre cada arco
    for edge in lt.iterator(lt_edges):
        bus = edge["Bus_Stop"].replace(" ", "").split("-")[1]
        station_i = edge["Code"] + "-" + bus
        station_f = edge["Code_Destiny"] + "-" + bus
        # si existe el vertice de salida y el vertice de llegada se crea un arco entre las dos estaciones
        if gr.containsVertex(gr_stations, station_i) and gr.containsVertex(gr_stations, station_f):
            # calcula la distancia entre dos puntos y lo agrega al vertice como la distancia
            v_station_i = me.getValue(mp.get(mp_stations, station_i))
            v_station_f = me.getValue(mp.get(mp_stations, station_f))
            lon_1, lat_1 = float(v_station_i["Longitude"]), float(v_station_i["Latitude"])
            lon_2, lat_2 = float(v_station_f["Longitude"]), float(v_station_f["Latitude"])

            distancia = harvesineDistance(lon_1, lat_1, lon_2, lat_2)
            gr.addEdge(gr_stations, station_i, station_f, distancia)
            gr.addEdge(digr_stops, station_i, station_f, 1)

def harvesineDistance(lon_1, lat_1, lon_2, lat_2):
    delta_lon = lon_2 -lon_1
    delta_lat = lat_2 - lat_1

    r = 6371
    rad = math.pi/180
    raiz = (math.sin(rad*delta_lat/2))**2 + math.cos(rad*lat_1) * math.cos(rad*lat_2) * (math.sin(rad*delta_lon/2))**2
    distancia = 2 * r * math.asin(math.sqrt(raiz))

    return distancia

# Funciones para creacion de datos

def loadData(catalog):
    gr_stations = catalog["gr_stations"]
    mp_stations = catalog["mp_stations"]
    lt_vertices = gr.vertices(gr_stations)
    lt_add = catalog["lt_vertices"]
    stations_u = 0
    stations_c = 0
    buses_c = 0
    format_output = []

    # recorre cada codigo del vertice
    for vertice in lt.iterator(lt_vertices):
        # si el vertice no es transbordo se suma al contador de estaciones unicas
        if vertice[0:1] != "T":
            stations_u += 1
        # si el vertice es transbordo se suma al contador de estaciones compartidas
        else:
            stations_c += 1
            # obtiene los arcos adyacentes de la estacion transbordo
            buses_c += lt.size(gr.adjacentEdges(gr_stations, vertice)) * 2

    # obtiene el numero de arcos totales y los resta a los arcos compartidos
    buses_u = gr.numEdges(gr_stations) - buses_c

    # obtiene los 5 primeros y 5 ultimos codigos de vertices agregados al grafo
    first_five = lt.subList(lt_add, 1, 5)
    last_five = lt.subList(lt_add, lt.size(lt_add) - 4, 5)

    for item in lt.iterator(last_five):
        lt.addLast(first_five, item)

    #recorre los 5 primeros y ultimos codigos de vertices
    for item in lt.iterator(first_five):
        v_vertice = me.getValue(mp.get(mp_stations, item))
        # encuentra los arcos de llegada y salida y los agrega al diccionario
        v_vertice["In Degree"] = gr.indegree(gr_stations, item)
        v_vertice["Out Degree"] = gr.outdegree(gr_stations, item)
        node_id = {"Node_Id": item}
        dict_out = node_id | v_vertice
        format_output.append(dict_out)

    return stations_u, stations_c, gr.numVertices(gr_stations), buses_u, buses_c, gr.numEdges(gr_stations), format_output

# Funciones de consulta

# Requerimiento 1
def routeStations(catalog, station_i, station_f):
    gr_stations = catalog["gr_stations"]
    paths = djk.Dijkstra(gr_stations, station_i)
    lt_stations_t = lt.newList("ARRAY_LIST")
    steps = []
    stations_t, tranfers_t = 0,0

    if djk.hasPathTo(paths, station_f):
        path = djk.pathTo(paths, station_f)

        while not st.isEmpty(path):
                step = st.pop(path)
                # se agraga el paso a la salida
                steps.append({
                    "Estacion inicial": step["vertexA"],
                    "Siguiente estacion": step["vertexB"],
                    "Distancia": step["weight"]
                    })

                if not lt.isPresent(lt_stations_t, step["vertexA"]):
                    lt.addLast(lt_stations_t, step["vertexA"])
                if not lt.isPresent(lt_stations_t, step["vertexB"]):
                    lt.addLast(lt_stations_t, step["vertexB"])

        distance = djk.distTo(paths, station_f)

        stations_t, tranfers_t = countStationTranfers(lt_stations_t)

    return distance, station_f, stations_t, tranfers_t, steps

# Requerimiento 2
def fewStops(catalog, station_i, station_f):
    digr_stops = catalog["digr_stops"]
    paths = djk.Dijkstra(digr_stops, station_i)
    mp_stations = catalog["mp_stations"]
    lt_stations_t = lt.newList("ARRAY_LIST")
    steps = []
    distance_t = 0
    stations_t, tranfers_t = 0,0

    if djk.hasPathTo(paths, station_f):
        path = djk.pathTo(paths, station_f)

        while not st.isEmpty(path):
            step = st.pop(path)
            v_station_i = me.getValue(mp.get(mp_stations, step["vertexA"]))
            v_station_f = me.getValue(mp.get(mp_stations, step["vertexB"]))
            lon_1, lat_1 = float(v_station_i["Longitude"]), float(v_station_i["Latitude"])
            lon_2, lat_2 = float(v_station_f["Longitude"]), float(v_station_f["Latitude"])
            distance = harvesineDistance(lon_1, lat_1, lon_2, lat_2)
            # se agraga el paso a la salida
            steps.append({
                "Estacion inicial": step["vertexA"],
                "Siguiente estacion": step["vertexB"],
                "Distancia": distance
                })

            if not lt.isPresent(lt_stations_t, step["vertexA"]):
                lt.addLast(lt_stations_t, step["vertexA"])
            if not lt.isPresent(lt_stations_t, step["vertexB"]):
                lt.addLast(lt_stations_t, step["vertexB"])

            distance_t += distance

        # realiza un conteo de las estaciones y transbordos
        stations_t, tranfers_t = countStationTranfers(lt_stations_t)

    return distance_t, stations_t, tranfers_t, steps

# Requerimiento 3
def component(catalog):
    catalog['mp_stations'] = scc.KosarajuSCC(catalog['gr_stations'])
    return scc.connectedComponents(catalog['mp_stations'])

# Requerimiento 4
def planShortRoute(catalog, lon_i, lat_i, lon_f, lat_f):
    gr_stations = catalog["gr_stations"]
    mp_stations = catalog["mp_stations"]
    lt_vertices = catalog["lt_vertices"]
    lt_station_i = lt.newList("ARRAY_LIST")
    lt_station_f = lt.newList("ARRAY_LIST")
    lt_stations_t = lt.newList("ARRAY_LIST")
    steps = []
    distance_t = 0
    stations_t = 0
    tranfers_t = 0

    # recorre cada vertice del grafo
    for station in lt.iterator(lt_vertices):
        # si la estacion no es un transbordo calcula la distancia del las estaciones de entreda a las estaciones de los vertices
        if station[0:1] != "T":
            v_station = me.getValue(mp.get(mp_stations, station))
            lon_s, lat_s = float(v_station["Longitude"]), float(v_station["Latitude"])

            distance_i = harvesineDistance(lon_i, lat_i, lon_s, lat_s)
            lt.addLast(lt_station_i, [distance_i, station])
            distance_f = harvesineDistance(lon_f, lat_f, lon_s, lat_s)
            lt.addLast(lt_station_f, [distance_f, station])

    # ordena de menor a mayor las estaciones en funcion de la distancia
    shs.sort(lt_station_i, compareDistance)
    shs.sort(lt_station_f, compareDistance)

    near_stationi = lt.getElement(lt_station_i, 1)
    near_stationf = lt.getElement(lt_station_f, 1)
    station_i = near_stationi[1]
    station_f = near_stationf[1]
    # calcula el camino mas corto desde un vertice de inicio
    paths = djk.Dijkstra(gr_stations, station_i)

    # si existe el camino al vertice busca el camino al vertice final
    if djk.hasPathTo(paths, station_f):
        path = djk.pathTo(paths, station_f)
        # mientras la pila del camino no este vacia se elimina un elemento
        while not st.isEmpty(path):
            step = st.pop(path)
            # se agraga el paso a la salida
            steps.append({
                "Estacion inicial": step["vertexA"],
                "Siguiente estacion": step["vertexB"],
                "Distancia": step["weight"]
                })

            # se agregan los vertices que se visitaron
            if not lt.isPresent(lt_stations_t, step["vertexA"]):
                lt.addLast(lt_stations_t, step["vertexA"])
            if not lt.isPresent(lt_stations_t, step["vertexB"]):
                lt.addLast(lt_stations_t, step["vertexB"])
        # encuentra la distancia desde el vertice inicial al vertice final
        distance_t = djk.distTo(paths, station_f)

    # realiza un conteo de las estaciones y transbordos
    stations_t, tranfers_t = countStationTranfers(lt_stations_t)

    return station_i.split("-")[0], near_stationi[0], station_f.split("-")[0], near_stationf[0], distance_t, stations_t, tranfers_t, steps

# Requerimiento 5
def reachable_stations(catalog: dict, id_org: str, num_max: int):
    graph_digr_stops = catalog['digr_stops']
    mp_stations = catalog['mp_stations']

    paths = djk.Dijkstra(graph_digr_stops, id_org)
    vertices = gr.vertices(graph_digr_stops)
    lst = lt.newList('ARRAY_LIST')
    format_list = []

    for vertex in lt.iterator(vertices):
        dist_to = djk.distTo(paths, vertex)
        if djk.hasPathTo(paths, vertex) and (dist_to <= num_max) and (dist_to != 0):
            lt.addLast(lst, vertex)

    for vertex in lt.iterator(lst):
        longitud = djk.distTo(paths, vertex)
        v_station_i = me.getValue(mp.get(mp_stations, vertex))
        lon_1, lat_1 = float(v_station_i["Longitude"]), float(v_station_i["Latitude"])
        format_list.append({
            "station": vertex,
            "latitude": lat_1,
            "longitude": lon_1,
            "steps": longitud
        })

    return format_list


# Requrimiento 6
def routeStationNH(catalog, station_i, nh):
    gr_stations = catalog["gr_stations"]
    mp_nh = catalog["mp_nh"]
    lt_dist_stations = lt.newList("ARRAY_LIST")
    paths = djk.Dijkstra(gr_stations, station_i)
    lt_nh = me.getValue(mp.get(mp_nh, nh))

    for stop in lt.iterator(lt_nh):
        station = stop["Code"]
        bus = stop["Bus_Stop"].replace(" ", "").split("-")[1]
        code_ruta = station + "-" + bus
        if djk.hasPathTo(paths, code_ruta) and (code_ruta != station_i) and (code_ruta[0:1] != "T"):
            dist = djk.distTo(paths, code_ruta)
            lt.addLast(lt_dist_stations, [dist, code_ruta])

    shs.sort(lt_dist_stations, compareDistance)
    station_f = lt.getElement(lt_dist_stations, 1)[1]

    return routeStations(catalog, station_i, station_f)


# Requerimiento 7
def circularPath(catalog, station_i):
    gr_stations = catalog["gr_stations"]
    lt_vertices = catalog["lt_vertices"]
    lt_path_i = lt.newList("ARRAY_LIST")
    lt_path_f = lt.newList("ARRAY_LIST")
    paths_i = djk.Dijkstra(gr_stations, station_i)
    steps_i = []
    steps_f = []
    find = False
    tranfers_t = 0
    stations_t = 0
    distance = 0

    for station_f in lt.iterator(lt_vertices):
        if djk.hasPathTo(paths_i, station_f) and (not find) and station_i != station_f and station_f[0:1] != "T":
            paths_f = djk.Dijkstra(gr_stations, station_f)
            if djk.hasPathTo(paths_f, station_i):
                find = True
                path_i = djk.pathTo(paths_i, station_f)
                path_f = djk.pathTo(paths_f, station_i)
                distance = djk.distTo(paths_i, station_f) + djk.distTo(paths_f, station_i)

                values = [{"path": path_i, "steps": steps_i, "lt_path": lt_path_i}, {"path": path_f, "steps": steps_f, "lt_path": lt_path_f}]

                for i in range(0,2):
                    while not st.isEmpty(values[i]["path"]) and find == True:
                        step = st.pop(values[i]["path"])
                        values[i]["steps"].append({
                                "Estacion inicial": step["vertexA"],
                                "Siguiente estacion": step["vertexB"],
                                "Distancia": step["weight"]
                                })

                        if not lt.isPresent(values[i]["lt_path"], step["vertexA"]):
                            lt.addLast(values[i]["lt_path"], step["vertexA"])
                        if not lt.isPresent(values[i]["lt_path"], step["vertexB"]):
                            lt.addLast(values[i]["lt_path"], step["vertexB"])

                # realiza un conteo de las estaciones y transbordos
                for station in lt.iterator(lt_path_i):
                    if station[0:1] == "T":
                        tranfers_t += 1
                    else:
                        stations_t += 1

                for station in lt.iterator(lt_path_f):
                    if station[0:1] == "T":
                        tranfers_t += 1
                    else:
                        stations_t += 1

    return distance, stations_t, tranfers_t, steps_i, steps_f

# Funciones de ordenamiento

def compareDistance(distance_1, distance_2):
    return distance_1[0] < distance_2[0]

# Funciones auxiliares

def countStationTranfers(lt_stations):
    tranfers_t = 0
    stations_t = 0
    for station in lt.iterator(lt_stations):
            if station[0:1] == "T":
                tranfers_t += 1
            else:
                stations_t += 1
    return stations_t, tranfers_t


# funciones para tests

def getTime():
    # retorna el tiempo en milisegundos
    return float(time.perf_counter()*1000)

def deltaTime(tFinal, tInicial):
    # delta time
    return tFinal - tInicial