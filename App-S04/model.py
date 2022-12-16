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
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dfs
from DISClib.Algorithms.Graphs import bfs
import random
import operator

assert cf
from  math import *
import sys

from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster

import operator

sys.setrecursionlimit(10000)


"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    analyzer = {'graph':None,
                'listaestaciones':None,
                'listarutas':None,
                'mapEdges':None,
                'vertexInfoMap':None,
                }

    analyzer['listaestaciones'] = lt.newList(datastructure= "ARRAY_LIST")

    analyzer['listarutas'] = lt.newList(datastructure= "ARRAY_LIST")

    analyzer['graph'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=100,
                                              )
    
    analyzer['edges'] = mp.newMap(numelements = 14000,
                                            maptype="PROBING",
                                            )

    analyzer["vertexInfoMap"] = mp.newMap(numelements = 14000,
                                            maptype="PROBING",
                                            )
    analyzer['paths']= mp.newMap(numelements = 14000,
                                            maptype="PROBING",
                                            )
    analyzer['components']= mp.newMap(numelements = 200,
                                            maptype="PROBING",
                                            )
    return analyzer
# Funciones para agregar informacion al catalogo


def addStop(catalog, stopsfile):
    catalog["listaestaciones"] = lt.newList(datastructure="ARRAY_LIST", filename=stopsfile)
    return catalog

def addRoute(catalog, routesfile):
    catalog["listarutas"] = lt.newList(datastructure="ARRAY_LIST", filename=routesfile)
    return catalog


def addStopsBig(catalog):
    for i in range(0, len(catalog[0]['listaestaciones']['elements'])):
        addBusStop(catalog, catalog[0]['listaestaciones']['elements'][i]['Code'], catalog[0]['listaestaciones']['elements'][i]['Bus_Stop'])
    for i in range(0, len(catalog[1]['listarutas']['elements'])):
        updateRoutesEdges(catalog, catalog[1]['listarutas']['elements'][i]["inicioid"], catalog[1]['listarutas']['elements'][i]["finalid"], catalog[1]['listarutas']['elements'][i]["weight"])

    return catalog



def addBusStop(catalog, code, idruta ):
    stopid = str(idruta).split("-")

    nombreStop = str(code)+ '-' + stopid[1]
    if not gr.containsVertex(catalog[0]['graph'], nombreStop):
        gr.insertVertex(catalog[0]['graph'], nombreStop)

    
    return catalog

def updateRoutesEdges(catalog, initialStation, finalstation, info):

    edges = catalog[0]['edges']

    route= initialStation + '&' + finalstation

    encuentra = mp.get(catalog[0]['edges'], route)

    if encuentra == None:
        mp.put(edges,route,info)
    return catalog

def addEdges(catalog):
    edges = catalog[0]['edges']
    graph = catalog[0]['graph']
    listedges = mp.keySet(edges)
    
    for key in lt.iterator(listedges):
        keyvalue = mp.get(edges, key)
        value = me.getValue(keyvalue)
        weight = value
        pos = key.find('&')
        size = len(key)
        idinicial = key[0:pos]
        idfinal=key[pos+1:size]
        gr.addEdge(graph, idinicial, idfinal, weight)

    return catalog


def haversine (lat1, lat2, lon1, lon2):
    longitud = lon2-lon1
    latitud = lat2-lat1
    a = sin(latitud/2)**2 + cos(lat1) * cos(lat2) * sin(longitud/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    base = 6317 * c
    return base

def calculaterouteweight(catalog):
    
    listarutas = catalog[1]["listarutas"]["elements"]
    listaestaciones = catalog[0]["listaestaciones"]["elements"]
    for i in range(0, len(listarutas)):
        inicio = listarutas[i]["Code"]
        bususo = listarutas[i]["Bus_Stop"]
        final = listarutas[i]["Code_Destiny"]
        stopid = str(bususo).split("-")
        listarutas[i]["inicioid"] = str(inicio) + "-" + str(stopid[1])
        listarutas[i]["finalid"] = str(final) +"-"+ str(stopid[1])

    for i in range(0, len(listaestaciones)): 
        code = listaestaciones[i]["Code"]
        busid = str(listaestaciones[i]["Bus_Stop"]).split("-")
        idfinal = str(code) + "-" + str(busid[1])
        listaestaciones[i]["idfinal"] = idfinal


    for i in range(0, len(listarutas)):
        for j in range(0, len(listaestaciones)):
            if listarutas[i]["inicioid"] == listaestaciones[j]["idfinal"]:
                latinicial = listaestaciones[j]["Latitude"]
                longinicial = listaestaciones[j]["Longitude"]
            if listarutas[i]["finalid"] == listaestaciones[j]["idfinal"]:
                latfinal = listaestaciones[j]["Latitude"]
                longfinal = listaestaciones[j]["Longitude"]
        weight = haversine(float(latinicial), float(latfinal), float(longinicial), float(longfinal))
        listarutas[i]["weight"] = weight

    return catalog 

def addEdgesTransbordo(catalog):
    listausar = catalog[0]['listaestaciones']["elements"]
    for i in range(0, len(listausar)):
        if listausar[i]["Transbordo"] == "S":
            codigobus = listausar[i]['Code']
            for j in range(0, len(listausar)):
                if listausar[i]['Bus_Stop'] != listausar[j]["Bus_Stop"]: 
                    if codigobus == listausar[j]["Code"]:
                        infovertexa = listausar[i]['Bus_Stop'].split("-")
                        vertexa = str(listausar[i]['Code']) + "-"+ infovertexa[1]
                        infovertexb = listausar[j]['Bus_Stop'].split("-")
                        vertexb = str(listausar[j]['Code']) + "-"+ infovertexb[1]
                        verticecompleto = vertexa + "&" + vertexb
                        mp.put(catalog[0]['edges'], verticecompleto, 0)
    return catalog

# Funciones para creacion de datos


# Funciones de consulta

def pathStationsBFS1(catalog, initialStation, finalstation):
    catalog[0]['paths'] = bfs.BreadhtFisrtSearch(catalog[0]['graph'], initialStation)
    hasPath = bfs.hasPathTo(catalog[0]['paths'], finalstation)
    if hasPath == True: 
        path = bfs.pathTo(catalog[0]['paths'], finalstation)
        pathfin = lt.newList(datastructure="ARRAY_LIST")
        for i in lt.iterator(path):
            lt.addLast(pathfin, i)
    else: 
        pathfin = "No hay camino"
    return pathfin

#REQ 1
def pathStationsDFS(catalog, initialStation, finalstation):
    catalog[0]['paths'] = dfs.DepthFirstSearch(catalog[0]['graph'], finalstation)
    hasPath = dfs.hasPathTo(catalog[0]['paths'], initialStation)
    if hasPath == True: 
        path = dfs.pathTo(catalog[0]['paths'], initialStation)
        pathfin = lt.newList(datastructure="ARRAY_LIST")
        for i in lt.iterator(path):
            lt.addLast(pathfin, i)
    else: 
        pathfin = "No hay camino"
    
    totaldistancia = 0
    listarutas = catalog[1]['listarutas']['elements']
    for i in range(0, pathfin['size']-1):
            for k in range(0,len(listarutas)):
                if listarutas[k]['Code'] == pathfin['elements'][i][0:3]:
                    if listarutas[k]['Code_Destiny'] == pathfin['elements'][i+1][0:3]:
                        bus = (listarutas[k]['Bus_Stop']).split("-")
                        bususo = pathfin['elements'][i].split("-")
                        if bus[1] == bususo[1]:
                            totaldistancia += listarutas[k]['weight']
    transbordos = 0
    totalparadas = pathfin['size']

    for i in range(0, totalparadas-1):
            elemento = pathfin['elements'][i].split("-")
            elemento2 = pathfin['elements'][i+1].split("-")
            if elemento[1] != elemento2[1]: 
                transbordos += 1

    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]
    for j in range(0,len(pathfin['elements'])):
        est_evaluar = (pathfin['elements'][j])
        for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        lat=float(lat)
                        long= float(long)

                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-1.html")

    
    return pathfin['elements'], totaldistancia, totalparadas, transbordos   
            

    

#REQ 2
def pathStationsBFS(catalog, initialStation, finalstation):
    catalog[0]['paths'] = bfs.BreadhtFisrtSearch(catalog[0]['graph'], finalstation)
    hasPath = bfs.hasPathTo(catalog[0]['paths'], initialStation)
    if hasPath == True: 
        path = bfs.pathTo(catalog[0]['paths'], initialStation)
        pathfin = lt.newList(datastructure="ARRAY_LIST")
        for i in lt.iterator(path):
            lt.addLast(pathfin, i)
    else: 
        pathfin = "No hay camino"

    totaldistancia = 0
    listarutas = catalog[1]['listarutas']['elements']

    for i in range(0, pathfin['size']-1):
            for k in range(0,len(listarutas)):
                if listarutas[k]['Code'] == pathfin['elements'][i][0:3]:
                    if listarutas[k]['Code_Destiny'] == pathfin['elements'][i+1][0:3]:
                        bus = (listarutas[k]['Bus_Stop']).split("-")
                        bususo = pathfin['elements'][i].split("-")
                        if bus[1] == bususo[1]:
                            totaldistancia += listarutas[k]['weight']
    transbordos = 0
    totalparadas = pathfin['size']

    for i in range(0, totalparadas-1):
            elemento = pathfin['elements'][i].split("-")
            elemento2 = pathfin['elements'][i+1].split("-")
            if elemento[1] != elemento2[1]: 
                transbordos += 1

    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]
    for j in range(0,len(pathfin['elements'])):
        est_evaluar = (pathfin['elements'][j])
        for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        lat=float(lat)
                        long= float(long)

                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-2.html")

    return pathfin['elements'], totaldistancia, totalparadas, transbordos   




#REQ 3
def connectedComponenets(catalog):
    catalog[0]['components'] = scc.KosarajuSCC(catalog[0]['graph'])
    numeroComponentes = scc.connectedComponents(catalog[0]['components'])

    listausar = catalog[0]['components']['idscc']['table']['elements']
    lista = lt.newList(datastructure='ARRAY_LIST')

    repeticiones = {}

    for i in range(0, len(listausar)):
        lt.addLast(lista, listausar[i]['value'])

    for j in lista['elements']: 
        if j in repeticiones: 
            repeticiones[j] += 1
        else: 
            repeticiones[j] = 1
    
    mapacomps = mp.newMap(maptype="PROBING")

    organizar = sorted(repeticiones.items(), key = operator.itemgetter(1), reverse =True)
    

    for m in range(1, 6):
        listaporcomponente = lt.newList(datastructure="ARRAY_LIST")
        for n in range(0, len(listausar)):
            if listausar[n]['value'] == organizar[m][0]:
                lt.addLast(listaporcomponente, listausar[n]['key'])
        
        mp.put(mapacomps, organizar[m][0], listaporcomponente)

 
    return numeroComponentes, mapacomps, organizar

def connectedCompon(catalog):
    catalog[0]['components'] = scc.KosarajuSCC(catalog[0]['graph'])
    numeroComponentes = scc.connectedComponents(catalog[0]['components'])

    listausar = catalog[0]['components']['idscc']['table']['elements']
    lista = lt.newList(datastructure='ARRAY_LIST')

    repeticiones = {}

    for i in range(0, len(listausar)):
        lt.addLast(lista, listausar[i]['value'])

    for j in lista['elements']: 
        if j in repeticiones: 
            repeticiones[j] += 1
        else: 
            repeticiones[j] = 1

    organizar = sorted(repeticiones.items(), key = operator.itemgetter(1), reverse =True)
    listaporcomponente = lt.newList(datastructure="ARRAY_LIST")
    for i in range(1, 6):
        for j in range(0, len(listausar)):
            if listausar[j]['value'] == organizar[i][0]:
                lt.addLast(listaporcomponente, listausar[j]['key'])

    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]

    for j in range(0,len(listaporcomponente['elements'])):
        est_evaluar = (listaporcomponente['elements'][j])
        for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        lat=float(lat)
                        long= float(long)

                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-3.html")

    return "Ya se puede visualizar el mapa"

#REQ 4
def shortestPath(catalog, originlong, originlat, destlong, destlat):
    listaestaciones=catalog[0]['listaestaciones']["elements"]
    primerlong=listaestaciones[0]["Longitude"]
    primerLat=listaestaciones[0]["Latitude"]
    distanciaoriginal=haversine(float(originlat), float(primerLat), float(originlong), float(primerlong))
    for i in range(0, len(listaestaciones)):
        lat=listaestaciones[i]["Latitude"]
        long=listaestaciones[i]["Longitude"]
        distancia_actual=haversine(float(originlat), float(lat), float(originlong), float(long))
        if distancia_actual<distanciaoriginal:
            distanciaoriginal=distancia_actual 
            idestacionorigen=listaestaciones[i]["idfinal"]
            latestacionorigen=listaestaciones[i]["Latitude"]
            longestacionorigen=listaestaciones[i]["Longitude"]
            busorigen=listaestaciones[i]["Bus_Stop"]


    listaposible=lt.newList(datastructure='ARRAY_LIST')
    distanciaoriginaldest=haversine(float(destlat), float(primerLat), float(destlong), float(primerlong))
    for i in range(0, len(listaestaciones)):
        lat=listaestaciones[i]["Latitude"]
        long=listaestaciones[i]["Longitude"]
        distanciaactualdest=haversine(float(destlat), float(lat), float(destlong), float(long))
        if distanciaactualdest<distanciaoriginaldest:
            distanciaoriginaldest=distanciaactualdest
           
            idestaciondestino=listaestaciones[i]["idfinal"]
            lt.addFirst(listaposible, listaestaciones[i])
   
   
    for i in range(0, len(listaposible["elements"])):
        valor=pathStationsBFS1(catalog, idestacionorigen, listaposible["elements"][i]["idfinal"])
        if valor != "No hay camino":
            latestaciondestino=listaposible["elements"][i]["Latitude"]
            longestaciondestino=listaposible["elements"][i]["Longitude"]
            distanciaresultado=haversine(float(destlat), float(latestaciondestino), float(destlong), float(longestaciondestino))
            break  
   
   
    totalestaciones=len(valor["elements"])
    listainforutas=lt.newList(datastructure="ARRAY_LIST")
    for i in range(0, len(valor["elements"])):
        for j in range(0, len(listaestaciones)):
            if listaestaciones[j]["idfinal"]==valor["elements"][i]:
                lt.addFirst(listainforutas, listaestaciones[j])
    contadortransbordo=0
   
    for i in range(0, len(listainforutas["elements"])):
        if listainforutas["elements"][i]["Transbordo"]=="S":
            contadortransbordo=contadortransbordo+1
    distanciaestaciones=0
    for i in range(1, len(listainforutas["elements"])):
        print("Identificador de la estacion "+str(i)+": "+ str(listainforutas["elements"][i-1]["idfinal"]))
        latanterior=listainforutas["elements"][i-1]["Latitude"]
        longanterior=listainforutas["elements"][i-1]["Longitude"]
        latactual=listainforutas["elements"][i]["Latitude"]
        longactual=listainforutas["elements"][i]["Longitude"]
        distanciasiguiente=haversine(float(latanterior), float(latactual), float(longanterior), float(longactual))
        distanciaestaciones=distanciaestaciones+distanciasiguiente
       
        print("La distancia entre la estacion "+ str(listainforutas["elements"][i-1]["idfinal"]) + " y "+ str(listainforutas["elements"][i]["idfinal"])+ " es de: "+ str( distanciasiguiente))
    print("Identificador de la estacion "+str(len(listainforutas["elements"]))+": "+ str(listainforutas["elements"][-1]["idfinal"]))
   
    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]
    for j in range(0,len(valor['elements'])):
        est_evaluar = (valor['elements'][j])
        for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        lat=float(lat)
                        long= float(long)

                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-4.html")

       
    return distanciaoriginal, distanciaestaciones, distanciaresultado, totalestaciones, contadortransbordo

#REQ 5
def path_Station_number(catalog, Station, number):
    catalog[0]['paths'] = bfs.BreadhtFisrtSearch(catalog[0]['graph'], Station)

    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]

    for i in range(0,len((catalog[0]['paths']['visited']['table']['elements']))):
        if str((catalog[0]['paths']['visited']['table']['elements'][i]['key'])) != "None":
            if int((catalog[0]['paths']['visited']['table']['elements'][i]['value']['distTo'])) < int(number):
                print(" ")
                print("Identificador de la estación: ")
                est_evaluar= catalog[0]['paths']['visited']['table']['elements'][i]['key']
                print(est_evaluar)
                print(" ")
                print("Número de conexiones: ")
                print(catalog[0]['paths']['visited']['table']['elements'][i]['value']['distTo'])

                for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        print(" ")
                        print("Latitud: ")
                        print(lat)
                        print(" ")
                        print("Longitud: ")
                        print(long)
                        print(" ")
                        print("_____________________")
                        lat= float(lat)
                        long= float(long)
                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-5.html")


#REQ 6
def shortestNeighborhood(catalog, estacionorigen, vecindario):
    listaestaciones=catalog[0]['listaestaciones']["elements"]
    listaNeighborhood=lt.newList(datastructure="ARRAY_LIST")
   
    for i in range(0, len(listaestaciones)):
        if(str(listaestaciones[i]["Neighborhood_Name"])==vecindario):
            lt.addLast(listaNeighborhood, listaestaciones[i])
    for i in range(0, len(listaestaciones)):
        if(listaestaciones[i]["idfinal"]==estacionorigen):
            latorigen=listaestaciones[i]["Latitude"]
            longorigen=listaestaciones[i]["Longitude"]
   
    primerlong=listaNeighborhood["elements"][0]["Longitude"]
    primerLat=listaNeighborhood["elements"][0]["Latitude"]
    listaposible=lt.newList(datastructure="ARRAY_LIST")
    distanciaprimera=haversine(float(primerLat), float(latorigen), float(primerlong), float(longorigen))
    for i in range(0, len(listaNeighborhood["elements"])):
        lat=listaNeighborhood["elements"][i]["Latitude"]
        long=listaNeighborhood["elements"][i]["Longitude"]
        distanciaactual=haversine(float(lat), float(latorigen), float(long), float(longorigen))
        if distanciaactual<distanciaprimera:
            distanciaprimera=distanciaactual
           
            lt.addFirst(listaposible, listaNeighborhood["elements"][i])
   

    for i in range(0, len(listaposible["elements"])):
        valor=pathStationsBFS1(catalog, estacionorigen, listaposible["elements"][i]["idfinal"])
        if valor != "No hay camino":
            latestaciondestino=listaposible["elements"][i]["Latitude"]
            longestaciondestino=listaposible["elements"][i]["Longitude"]
            distanciaresultado=haversine(float(latorigen), float(latestaciondestino), float(longorigen), float(longestaciondestino))
            break  

    totalestaciones=valor["size"]
    listainforutas=lt.newList(datastructure="ARRAY_LIST")
    for i in range(0, len(valor["elements"])):
        for j in range(0, len(listaestaciones)):
            if listaestaciones[j]["idfinal"]==valor["elements"][i]:
                lt.addFirst(listainforutas, listaestaciones[j])
               
    contadortransbordo=0
   
   
    for i in range(0, len(listainforutas["elements"])):
        if listainforutas["elements"][i]["Transbordo"]=="S":
            contadortransbordo=contadortransbordo+1
    distanciaresultado=0
    for i in range(1, len(listainforutas["elements"])):
        print("Identificador de la estacion "+str(i)+": "+ str(listainforutas["elements"][i-1]["idfinal"]))
        print("Vecindario de la estacion "+str(listainforutas["elements"][i-1]["idfinal"])+ " es "+ str(listainforutas["elements"][i-1]["Neighborhood_Name"]))
        latanterior=listainforutas["elements"][i-1]["Latitude"]
        longanterior=listainforutas["elements"][i-1]["Longitude"]
        latactual=listainforutas["elements"][i]["Latitude"]
        longactual=listainforutas["elements"][i]["Longitude"]
        distanciasiguiente=haversine(float(latanterior), float(latactual), float(longanterior), float(longactual))
        distanciaresultado=distanciaresultado+distanciasiguiente
        print("La distancia entre la estacion "+ str(listainforutas["elements"][i-1]["idfinal"]) + " y "+ str(listainforutas["elements"][i]["idfinal"])+ " es de: "+ str( distanciasiguiente))
    print("Identificador de la estacion "+str(len(listainforutas["elements"]))+": "+ str(listainforutas["elements"][-1]["idfinal"]))
    print("Vecindario de la estacion "+str(listainforutas["elements"][-1]["idfinal"])+ " es "+ str(listainforutas["elements"][-1]["Neighborhood_Name"]))
    
    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]
    for j in range(0,len(valor['elements'])):
        est_evaluar = (valor['elements'][j])
        for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        lat=float(lat)
                        long= float(long)

                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-6.html")

    return distanciaresultado, totalestaciones, contadortransbordo

#REQ7 
def circularpath(catalog, station):
    #Uso de los componenetes conectados
    listconComp = (catalog[0]['components']['idscc']['table']['elements'])
    listaporcomp = lt.newList(datastructure='ARRAY_LIST')
    for i in range(0, len(listconComp)):
        if listconComp[i]['key'] == station:
            for j in range(0, len(listconComp)):
                if listconComp[i]['value'] == listconComp[j]['value']:
                    lt.addLast(listaporcomp, listconComp[j])
    
    m = random.randint(2,len(listaporcomp))

    catalog[0]['paths'] = bfs.BreadhtFisrtSearch(catalog[0]['graph'], station)
    hasPath = bfs.hasPathTo(catalog[0]['paths'], listaporcomp['elements'][m]['key'])
    if hasPath == True: 
        path = bfs.pathTo(catalog[0]['paths'], listaporcomp['elements'][m]['key'])
        pathfinal = lt.newList(datastructure="ARRAY_LIST")
        for i in lt.iterator(path):
            lt.addLast(pathfinal, i)

    catalog[0]['paths'] = bfs.BreadhtFisrtSearch(catalog[0]['graph'], listaporcomp['elements'][m]['key'])
    hasPath = bfs.hasPathTo(catalog[0]['paths'], station)
    if hasPath == True: 
        path = bfs.pathTo(catalog[0]['paths'], station)
        pathend = lt.newList(datastructure="ARRAY_LIST")
        for i in lt.iterator(path):
            lt.addLast(pathend, i)

    pathfin = lt.newList(datastructure="ARRAY_LIST")

    for i in range(0, len(pathend['elements'])):
        lt.addLast(pathfin, pathend['elements'][i])
    
    for i in range(1, len(pathfinal['elements'])):
        lt.addLast(pathfin, pathfinal['elements'][i])

    totaldistancia = 0
    listarutas = catalog[1]['listarutas']['elements']

    for i in range(0, pathfinal['size']-1):
            for k in range(0,len(listarutas)):
                if listarutas[k]['Code'] == pathfinal['elements'][i][0:3]:
                    if listarutas[k]['Code_Destiny'] == pathfinal['elements'][i+1][0:3]:
                        bus = (listarutas[k]['Bus_Stop']).split("-")
                        bususo = pathfinal['elements'][i].split("-")
                        if bus[1] == bususo[1]:
                            totaldistancia += listarutas[k]['weight']
    transbordos = 0
    totalparadas = pathfin['size']

    for i in range(0, totalparadas-1):
            elemento = pathfin['elements'][i].split("-")
            elemento2 = pathfin['elements'][i+1].split("-")
            if elemento[1] != elemento2[1]: 
                transbordos += 1
    
    m = folium.Map(location=[41.3879, 2.16992], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    points=[]
    for j in range(0,len(pathfin['elements'])):
        est_evaluar = (pathfin['elements'][j])
        for j in range(0,len(catalog[0]['listaestaciones']['elements'])):
                    code= catalog[0]['listaestaciones']['elements'][j]['Code']
                    busStop= catalog[0]['listaestaciones']['elements'][j]['Bus_Stop']
                    busid = str(busStop).split("-")
                    idfinal = str(code) + "-" + str(busid[1])
                    if str(idfinal) == str(est_evaluar):
                        long = catalog[0]['listaestaciones']['elements'][j]['Longitude']
                        lat = catalog[0]['listaestaciones']['elements'][j]['Latitude']
                        lat=float(lat)
                        long= float(long)

                        points.append(tuple([lat,long]))
                        folium.Marker(location=[lat,long], popup="Estación",icon=folium.Icon(color="green", icon="ok-sign"),).add_to(marker_cluster)
    
    folium.PolyLine( points, color="red", weight =2.5, opacity=1).add_to(m)
    m.save("Mapa_REQ-7.html")

    return pathfin['elements'], totaldistancia, totalparadas, transbordos 


# Funciones utilizadas para comparar elementos dentro de una lista



# Funciones de ordenamiento
