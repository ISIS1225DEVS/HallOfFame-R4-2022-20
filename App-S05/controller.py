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
import datetime
import time
from DISClib.ADT import list as lt
from DISClib.ADT import graph as gr
from DISClib.ADT import map as mp



"""
El controlador se encarga de mediar entre la vista y el modelo.
"""
#* Configurar el entorno de desarrollo

csv.field_size_limit(2147483647)

# Inicialización del Catálogo de libros

def newController():
    """
    Llama la función para iniciar el Catalogo de Plataformas Digitales
    """
    
    control = {"model" : None}
    control["model"] = model.newAnalyzer()
    
    return control   

# Funciones para la carga de datos

def loadData(control, suffix):
    analyzer = control["model"]
    StopsFile = cf.data_dir + "bus_stops_bcn-utf8" + suffix
    EdgesDataFile = cf.data_dir + "bus_edges_bcn-utf8" + suffix
    inputFileStops = csv.DictReader(open(StopsFile, encoding = 'utf-8'))
    inputFileEdgesData = csv.DictReader(open(EdgesDataFile, encoding= "utf-8"))
    sizeStops = 0
    sizeRoutes = 0



    for stop in inputFileStops:
        sizeStops += 1

        reformStop(stop, analyzer)
    
        model.addCoordenadasToHASH(stop, analyzer)
        model.addNeighborhoodToHASH(stop, analyzer)
        model.addDistrictToHASH(stop, control['model'])
        model.addNeighToHASH(stop, control['model'])
        model.addVertexToGraph(stop, "DiGraph", analyzer)
        model.addVertexToGraph(stop, "graph", analyzer)
        # FUNCION PONER EDGES DE STOP A TRANSBORDO
        if stop["Transbordo"]=="S":
                model.addEdgeToTransbordo(stop,"graph", analyzer)
                model.addEdgeToTransbordo(stop,"DiGraph", analyzer)
                

    for edge in inputFileEdgesData:
        sizeRoutes +=1
        reformEdge(edge)
        model.addEdgesToGraph(edge, "DiGraph", analyzer)
        model.addEdgesToGraph(edge, "graph", analyzer)

            #ESTO ERA PARA CONFIRMAR SI HABÍAN REPETIDOS O NO JAJA
    # model.ordenarListasExperimento(analyzer)

    totalBusStops, exclusiveBusStops, sharedBusStops, totalBusStopsRoutes, exclusiveBusStopsRoutes, sharedBusRoutes = model.countExclusive(control['model'], sizeRoutes)

    totalRutas = model.countRutas(analyzer)

    area, longMin, longMax,  latMin, latMax = model.rangoArea(analyzer)

    table = model.firstAndLast5(analyzer["graph"], analyzer)

    nodes, edges = model.graphSpecs(control['model'], "DiGraph")

    DiGraphNodes = nodes
    DiGraphEdges = edges

    nodes, edges = model.graphSpecs(control['model'], "graph")

    graphNodes = nodes
    graphEdges = edges

    tableDiGraph = model.tableDiGraph(control['model'])
    tableGraph = model.tableGraph(control["model"])

    return control, totalRutas, area, longMin, longMax,  latMin, latMax, table, sizeStops , sizeRoutes, totalBusStops, exclusiveBusStops, sharedBusStops, totalBusStopsRoutes, exclusiveBusStopsRoutes, sharedBusRoutes, DiGraphEdges, DiGraphNodes, graphEdges, graphNodes, tableDiGraph, tableGraph

# Funciones de ordenamiento

def reformStop(stop, analyzer):
    addId(stop)
    stop["Longitude"] = float(stop["Longitude"])
    stop["Latitude"] = float(stop["Latitude"])

    ruta = stop["Bus_Stop"][4:]
    lt.addLast(analyzer["rutas LIST"], ruta)

    mapaLongitudes = analyzer["mapa de longitudes"]
    model.addCoord(stop["Longitude"], mapaLongitudes)

    mapaLatitudes = analyzer["mapa de latitudes"]
    model.addCoord(stop["Latitude"], mapaLatitudes)




def reformEdge(edge):
    convertCodes(edge)

def addId(stop):
    code = stop["Code"]
    bus = stop["Bus_Stop"].split("-")
    bus = bus[1]
    lenCode = len(code)
    missingCeros = "0"*(4-lenCode)

    newCode = missingCeros+code

    id = newCode + "-" + bus

    stop["id"] = id

def convertCodes(edge):
    columns = ["Code", "Code_Destiny"]

    for x in columns:
        code = edge[x]
        lenCode = len(code)
        missingCeros = "0"*(4-lenCode)
        newCode = missingCeros+code
        
        edge[x] = newCode

def mostrarCarga(control):
    a = ("Total estaciones transbordo: "+str(lt.size(control["model"]["listPerTransbordo"])))
    a += "\n"
    a += ("Total estaciones NO transbordo: "+str(lt.size(control["model"]["listPerNOTTransbordo"])))
    a += "\n"
    a += ("El total de arcos utilizados en todas las rutas de buses del grafo dirigido son: "+str(gr.numEdges(control["model"]["DiGraph"])))
    a += "\n"
    a += ("El total de arcos utilizados en todas las rutas de buses del grafo NO dirigido son: "+str(gr.numEdges(control["model"]["graph"])))
    a += "\n"
    return a
    


# Funciones de consulta sobre el catálogo

#! =^..^=   =^..^=   =^..^=    =^..^=  [función auxiliar 0]  =^..^=    =^..^=    =^..^=    =^..^=
def formateo(codigo):
    if codigo[0]=="T":
        return codigo
    codigo = codigo.split("-")
    partOne = str(codigo[0])
    partTwo = str(codigo[1])
    if len(partOne)!=4:
        partOne = "0"*(4-len(partOne))+partOne
    return (partOne+"-"+partTwo)

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 1]  =^..^=    =^..^=    =^..^=    =^..^=

def buscarCaminoPosibleEntreDosEstaciones(analyzer, graph, startStop, endStop):
    startStop = formateo(startStop)
    endStop = formateo(endStop)
    respuesta = model.buscarCaminoPosibleEntreDosEstaciones(analyzer[graph], startStop, endStop)
    return respuesta

        # NO SE HACE PORQUE SOLO SOMOS DOS

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 2]  =^..^=    =^..^=    =^..^=    =^..^=

def buscarCaminoOptimoEntreDosEstaciones(control, startStop, endStop):
    analyzer = control["model"]
    startStop = formateo(startStop)
    endStop = formateo(endStop)
    return model.buscarCaminoOptimoEntreDosEstaciones(analyzer, startStop, endStop)

def distancias(control,pathList):
    analyzer = control["model"]
    return model.distancias(analyzer,pathList)
#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 3]  =^..^=    =^..^=    =^..^=    =^..^=

def reconocerComponentesConectados(control):
    analyzer = control["model"]
    totalScc, table = model.reconocerComponentesConectados(analyzer)
    return totalScc, table

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 4]  =^..^=    =^..^=    =^..^=    =^..^=

def requerimientoCuatro(control,localizacionOrigen,localizacionDestino):
    listaBoba = localizacionOrigen.split(",")
    localizacionOrigen = (float(listaBoba[1].strip()),float(listaBoba[0].strip()))
    listaBoba = localizacionDestino.split(",")
    localizacionDestino = (float(listaBoba[1].strip()),float(listaBoba[0].strip()))
    analyzer = control["model"]
    return model.requerimientoCuatro(analyzer,localizacionOrigen,localizacionDestino)

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 5]  =^..^=    =^..^=    =^..^=    =^..^=

def reqCinco(control,estacionOrigen,numeroConexiones):
    estacionOrigen = formateo(estacionOrigen)
    analyzer = control["model"]
    return model.reqCinco(analyzer,estacionOrigen,int(numeroConexiones))


#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 6]  =^..^=    =^..^=    =^..^=    =^..^=

def requerimientoSix(control,estacionOrigen,neighborhoodDestino):
    estacionOrigen = formateo(estacionOrigen)
    analyzer = control["model"]
    return model.requerimientoSix(analyzer,estacionOrigen,neighborhoodDestino)

#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 7]  =^..^=    =^..^=    =^..^=    =^..^=
def findCirclePath(origin, control):
    origin = formateo(origin)
    analyzer = control['model']
    return model.findCirclePath(origin, analyzer)


#! =^..^=   =^..^=   =^..^=    =^..^=  [Requerimiento 8]  =^..^=    =^..^=    =^..^=    =^..^=


#* Funciones de Calculo y Analisis

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def deltaTime(end, start):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed

def printkeys(control):
    model.printkeys(control["model"])