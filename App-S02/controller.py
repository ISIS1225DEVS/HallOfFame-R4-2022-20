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
 """

import config as cf
import model
import csv
import numpy as np
from DISClib.ADT import list as lt


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros
def init():
    analyzer = model.newAnalyzer()
    return analyzer

def loadData(analyzer, id):
    #print(cf.data_dir)
    edgesfile = cf.data_dir + '/Barcelona_def/bus_edges_bcn-utf8-{}.csv'.format(id)
    stopsfile = cf.data_dir + '/Barcelona_def/bus_stops_bcn-utf8-{}.csv'.format(id)
    edges_file = csv.DictReader(open(edgesfile, encoding="utf-8"),
                                delimiter=",")
    stops_file = csv.DictReader(open(stopsfile, encoding="utf-8"),
                                delimiter=",")
    for stop in stops_file:
        bus_stop = (stop['Bus_Stop'].split("-"))[1].strip() # Saca el número del bus ***
        stop['ID'] = stop['Code'] + '-' + bus_stop # Pega el código de la estacion con el número del bus ***
        #print(stop)
        model.addStop(analyzer, stop)  
        model.addStopVertex(analyzer, stop)
        model.addLatitude(analyzer, stop)
        model.addLongitude(analyzer, stop)
        model.addRoute(analyzer, stop)
        info = model.getInfoLoad(analyzer, stop)
        if stop['Transbordo'] == 'S':
            #print('S')
            model.addRouteToEstation(analyzer, stop) 
        #else:
        #    print('T')
            
    for edge in edges_file:
        model.addConnection(analyzer, edge) 
    return analyzer, info

# Funciones para la carga de datos

# Funciones de ordenamiento

#Funciones Req1
def req1(origen, destino, cont):
    return model.req1(origen, destino, cont)

# Funciones de consulta sobre el catálogo
def getTotalRoutes(analyzer): 
    return model.getTotalRoutes(analyzer)

def getTotalRoutesExclus(analyzer): 
    return model.getTotalRoutesExclus(analyzer) 

def getTotalTransbordo(analyzer):
    return model.getTotalTransbordo(analyzer)

def getEdges(analyzer):
    return model.getEdges(analyzer)

def getMinlon(analyzer):
    return model.getMinlon(analyzer)

def getMinlat(analyzer):
    return model.getMinlat(analyzer)

def getMaxlon(analyzer):
    return model.getMaxlon(analyzer)

def getMaxlat(analyzer):
    return model.getMaxlat(analyzer)

def getVertex(analyzer):
    return model.getVertex(analyzer)

def getInfoLoad(analyzer, lst):
    return model.getInfoLoad(lst, analyzer)

def getFirstLast(lst, analyzer):
    return model.getFirstLast(lst, analyzer)

def getStopFromList(analyzer, stop):
    return model.getStopFromList(analyzer, stop)

#Funciones Req2
def req2(origen, destino, cont):
    return model.req2(origen, destino, cont) 

#Funciones Req4
def req4(origen, destino, cont):
    org,des,d_org,d_des = model.closest_est(origen, destino, cont)
    dist = [d_org,d_des]
    #print(org,des,d_org,d_des)
    return model.req4(org,des,dist,cont)
    #print(cont['stops'])

#Funciones Req5
def req5(origen,n,cont):
    return model.req5(origen,n,cont)

#Funciones Req6
def req6(origen,vecindario_destino,cont):
    return model.req6(origen,vecindario_destino,cont)

def req7(analyzer, origen):
    return model.req7(analyzer, origen)