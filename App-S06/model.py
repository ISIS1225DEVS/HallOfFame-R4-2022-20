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

from math import radians, cos, sin, asin, sqrt
from re import S
import config as cf
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.ADT import graph as gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
from datetime import datetime
assert cf
from DISClib.Algorithms.Sorting import quicksort as quick
from DISClib.Algorithms.Sorting import shellsort as shell
from DISClib.Algorithms.Sorting import selectionsort as selection
from DISClib.Algorithms.Sorting import insertionsort as insertion
from DISClib.Algorithms.Sorting import mergesort as merge


"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

def haversine(lon1, lat1, lon2, lat2):
            """
            Calculate the great circle distance in kilometers between two points 
            on the earth (specified in decimal degrees)
            """
            # convert decimal degrees to radians 
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

            # haversine formula 
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
            return c * r
        

def add_carga_bus_stops(model, st_code,station, bus_route,line_archive):
    # Agrega las estaciones y las Rutas de Bus
    model.addStation(station)
    model.addBusRoute(bus_route)
    if station.transbordo == "S":
        model.addGraphVertex("T-"+st_code)
    


def add_carga_bus_edges(model, line_archive):
    inicio  = line_archive["Code"]
    final   = line_archive["Code_Destiny"]
    id_ruta =line_archive["Bus_Stop"].replace('BUS-', '')

    vertice_inicio = inicio+"-"+id_ruta
    vertice_final  = final+"-"+id_ruta

    #model.addGraphVertex(inicio)
    #model.addGraphVertex(final)

    st_inicio =model.getStationByCode(line_archive["Code"])
    st_final = model.getStationByCode(line_archive["Code_Destiny"])

    st_inicio.addAyacente(st_final.code)
    st_final.addAyacente(st_inicio.code)

    lat1, lon1 = float(st_inicio.latitud), float(st_inicio.longitud)
    lat2, lon2 = float(st_final.latitud) , float(st_final.longitud)
    peso = haversine(lon1, lat1, lon2, lat2)
    model.addGraphEdge(vertice_inicio, vertice_final, peso)
    model.addGraphEdge(vertice_final,vertice_inicio, peso)
   

    '''
    inicio =model.getStationByCode(line_archive["Code"])
    final = model.getStationByCode(line_archive["Code_Destiny"])
    ##ruta =model.getBusByCode(line_archive["Bus_Stop"].replace('BUS-', ''))
    id_ruta =line_archive["Bus_Stop"].replace('BUS-', '')

    code_vertice_inicio =inicio.code + "-" + id_ruta
    code_vertice_final = final.code + "-" + id_ruta
    lat1, lon1 = float(inicio.latitud), float(inicio.longitud)
    lat2, lon2 = float(final.latitud), float(final.longitud)

    model.addGraphVertex(code_vertice_inicio)
    model.addGraphVertex(code_vertice_final)

    peso = haversine(lon1, lat1, lon2, lat2)
    #print(type(peso),peso)
    #print("Agregando Arco ",code_vertice_inicio, code_vertice_final, 0)
    model.addGraphEdge(code_vertice_inicio, code_vertice_final, peso)
    model.addGraphEdge( code_vertice_final,code_vertice_inicio, peso)
    #model.addGraphEdge( code_vertice_final,code_vertice_inicio, peso)
    if inicio.transbordo == "S":
        #print("Agregando Arco ",code_vertice_inicio,  "T-"+ inicio.code, peso)
        model.addGraphEdge(code_vertice_inicio, "T-"+ inicio.code,0)
        model.addGraphEdge("T-"+ inicio.code,code_vertice_inicio,0)
    if final.transbordo == "S":
        #print("Agregando Arco ",code_vertice_final,  "T-"+ final.code)
        model.addGraphEdge(code_vertice_final, "T-"+ final.code, 0)
        model.addGraphEdge("T-"+ final.code,code_vertice_final,  0)
    '''

def requerimiento_1(model, origen, destino):
    cola = None
    if model.graphHasPathTo(origen, destino, "djk"):
        cola, peso = model.graphPathTo(destino, "djk")
    return cola, peso

def requerimiento_2(model, origen, destino):
    cola = None
    peso = 0
    if model.graphHasPathTo(origen, destino, "bfs"):
        cola, peso = model.graphPathTo(destino,"bfs")
    return cola, peso
    
def requerimiento_3(model):
    model.MapaKosaraju()
    lista_valores, num_conected = model.GraphScc()
    return lista_valores, num_conected
    #for value in lt.iterator(lista_valores):
        #print(value["cont"], value["num"], lt.size(value["vertices"]))

def requerimiento_4(model, lonOrigen, latOrigen, lonDestino, latDestino):
    station_origen = model.estacionMasCercana(lonOrigen, latOrigen)
    station_destino= model.estacionMasCercana(lonDestino, latDestino)
    verticeOrigen = model.buscarVertice(station_origen)
    verticeDestino = model.buscarVertice(station_destino)
    print("verticeOrigen:", verticeOrigen)
    print("verticeDestino:", verticeDestino)

    print(model.graphHasPathTo(verticeOrigen, verticeDestino, "djk"))
    if model.graphHasPathTo(verticeOrigen, verticeDestino, "djk"):
        print("Si hay camino" )
        cola, peso = model.graphPathTo(verticeDestino,"djk")
        return cola, peso,verticeOrigen,verticeDestino
    return None,0,None,None
    #print("Si hay camino ",verticeOrigen,verticeDestino )

def requerimiento_6(model, vertice_origen, vecindario_destino):
  
    stations_list = model.estacionesDelVecindario(vecindario_destino)
    print("----- Posibles estaciones -------")
    for station in lt.iterator(stations_list):
        print("    " ,station)

    vertices_list =model.verticesDelVecindario(stations_list)
    print("----- Posibles vertices -------")
    for vertice in lt.iterator(vertices_list):
        print("    " ,vertice)

    cola = None
    mejor_peso  = 100000000
    mejor_ruta  = None
    mejor_largo = 10000000
    model.djk_search(vertice_origen)
    for verticeDestino in lt.iterator(vertices_list):
        if model.djk_hasPathTo(verticeDestino):
            cola, peso,largo = model.djk_pathTo(verticeDestino)
            #print("    ",peso,largo,verticeDestino)
            if peso <= mejor_peso  and largo < mejor_largo:
                #print("     win")
                mejor_ruta = cola
                mejor_peso = peso
                mejor_largo = largo

    return cola, mejor_peso, mejor_largo

def requerimiento_7(model, vertice_origen):
    cola = model.bfs(vertice_origen)
    #cola = model.req7(vertice_origen)
    #print(cola)
    return cola