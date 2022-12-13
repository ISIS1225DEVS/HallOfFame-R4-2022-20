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
import webbrowser
from DISClib.ADT import list as lt
assert cf
from tabulate import tabulate


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def newController():
    """
    Se crea una instancia del controlador
    """
    control = controller.newController()
    return control

def printTabulatedData(filteredData, headers, detailHeaders=any):
    size = lt.size(filteredData)
    table = []
    width = 21
    if size:
        for data in lt.iterator(filteredData):
            fields = []
            for header in headers:
                if type(data[header]) == dict:
                    detailsTable = []
                    for register in lt.iterator(controller.firstAndLastThreeData(data[header])):
                        details = []
                        for detailHeader in detailHeaders:
                            if register[detailHeader] == '':
                                details.append('Unknown')
                            else:
                                details.append(register[detailHeader])
                        detailsTable.append(details)
                    fields.append(tabulate(detailsTable, detailHeaders, tablefmt="grid", maxcolwidths=12))
                elif data[header] == '':
                    fields.append('Unknown')
                else:
                    fields.append(data[header])
            table.append(fields)
        if len(headers) <= 3:
            print(tabulate(table, headers, tablefmt="grid") + '\n')
        else:
            print(tabulate(table, headers, tablefmt="grid", maxcolwidths=width) + '\n')
    else:
        print('\nNo se encontró contenido con este criterio de busqueda\n')

def convertFeature(feature):
    if feature == '1':
        converted = 'Best Time'
    elif feature == '2':
        converted = 'Second Best Time'
    elif feature == '3':
        converted = 'Third Best Time'
    elif feature == '4':
        converted = 'Average Time'
    elif feature == '5':
        converted = 'Number Runs'
    else:
        converted = 'None'
    return converted

def convertAnswer(answer):
    converted = False
    if answer in ['1', 1, True, 'True', 'Yes']:
        converted = True
    return converted

def printMenu():
    print("Bienvenido")
    print("0- Cargar información en el catálogo")
    print("1- Encontrar los videojuegos publicados en un rango de tiempo para una plataforma")
    print("2- Encontrar los 5 registros con menor tiempo para un jugador en especifico")
    print("3- Conocer los registros más veloces en un rango de intentos")
    print("4- Conocer los registros más lentos dentro de un rango de fechas")
    print("5- Conocer los registros más recientes para un rango de tiempos récord")
    print("6- Diagramar un histograma de propiedades para los registros de un rango de anios")
    print("7- Encontrar el TOP N de los videojuegos más rentables para retransmitir")
    print("8- Graficar la distribución de las nacionalidades de los poseedores de los mejores tiempos para video juegos lanzados en un año")

analyzer = newController()
sizeFile = 'large'

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 0:
        print("\n\nCargando información de los archivos ....\n")
        startTime = controller.getTime()
        controller.loadData(analyzer, sizeFile)
        print('-'*52)
        print('Loaded speedrunning data properties...')
        print('Total loaded video games: ' + str(lt.size(analyzer['videoGames'])))
        print('Total loaded category records: ' + str(lt.size(analyzer['speedrunRecords'])))
        print('-'*52)
        filtered = controller.firstAndLastThreeData(analyzer['videoGames'])
        headers = ['Game_Id', 'Release_Date', 'Name', 'Abbreviation', 'Platforms', 'Total_Runs', 'Genres']
        print('\nThe first 3 and last 3 video games loaded in ADTs are...')
        print('Data from games displayed as read from CSV file')
        printTabulatedData(filtered, headers)
        filtered = controller.firstAndLastThreeData(analyzer['speedrunRecords'])
        headers = ['Game_Id', 'Record_Date_0', 'Num_Runs', 'Name', 'Category', 'Subcategory', 'Country_0', 'Players_0', 'Time_0']
        print('-'*52)
        print('\nThe first 3 and last 3 category records loaded in ADTs are...')
        print('Data from games displayed as read from CSV file')
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 1:
        platform = input('Platform: ')
        initialDate = input('Initial Date: ')
        finalDate = input('Final Date: ')
        startTime = controller.getTime()
        filtered, details = controller.getGamesByPlatformInDate(analyzer, platform, initialDate, finalDate)
        print('\n\n' + '='*15 + ' Req No. 1 Inputs ' + '='*15)
        print("Games released between '" + initialDate + "' and '" + finalDate +  "'")
        print("In platform: '" + platform + "'")
        print('\n' + '='*15 + ' Req No. 1 Answer ' + '='*15)
        print("Available games in '" + platform + "': " + str(details['gamesByPlatform']))
        print("Date range between '" + initialDate + "' and '" + finalDate +  "'")
        print('Released games: ' + str(details['gamesInRange']))
        print('\n' + '-'*6 + ' Video Games release details ' + '-'*6)
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        print('The first 3 and last 3 in range are:')
        filtered = controller.firstAndLastThreeData(filtered)
        headers = ['Release_Date', 'Count', 'Details']
        detailHeaders = ['Total_Runs', 'Name', 'Abbreviation', 'Platforms', 'Genres']
        printTabulatedData(filtered, headers, detailHeaders)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
    
    elif int(inputs[0]) == 2:
        player = input('Player: ')
        startTime = controller.getTime()
        filtered, details = controller.getRegistersByPlayer(analyzer, player)
        print('\n\n' + '='*15 + ' Req No. 2 Inputs ' + '='*15)
        print("Speedrun records for player: '" + player + "'")
        print('\n' + '='*15 + ' Req No. 2 Answer ' + '='*15)
        print("Player '" + player + "' has '" + str(details['attempsByPlayer']) + "' Speedrun record attemps")
        print('\n' + '-'*6 + " Player '" + player + "' details " + '-'*6)
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Time_0', 'Record_Date_0', 'Name', 'Players_0', 'Country_0', 'Num_Runs', 'Platforms', 'Genres', 'Category', 'Subcategory']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
    
    elif int(inputs[0]) == 3:
        limInf = int(input('Límite Inferior: '))
        limSup = int(input('Límite Superior: '))
        startTime = controller.getTime()
        filtered,details = controller.getFasterRecords(analyzer, limInf, limSup)
        print('\n\n' + '='*15 + ' Req No. 3 Inputs ' + '='*15)
        print("Category records between '" + str(limInf) + "' and '" + str(limSup) + "'")
        print('\n' + '='*15 + ' Req No. 3 Answer ' + '='*15)
        print("Attempts between '" + str(limInf) + "' and '" + str(limSup) + "'")
        print("Total records: " + str(details['Total_attemps']))
        print('\n' + '-'*7 + ' Videogame release details' + '-'*7)
        print("There are '" + str(lt.size(filtered)) + "' elements in range")
        filtered = controller.firstAndLastThreeData(filtered)
        headers = ['Num_Runs', 'Count', 'Details']
        detailHeaders = ['Time_0', 'Record_Date_0', 'Name', 'Players_0', 'Country_0', 'Platforms', 'Genres', 'Category', 'Subcategory', 'Release_Date']
        printTabulatedData(filtered, headers, detailHeaders)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 4:
        initialDate = input('Initial Date ')
        finalDate = input('Final Date: ')
        startTime = controller.getTime()
        filtered, details = controller.getRegistersByDates(analyzer, initialDate, finalDate)
        print('\n\n' + '='*15 + ' Req No. 4 Inputs ' + '='*15)
        print("Category records between '" + initialDate + "' and '" + finalDate + "' datetime.")
        print('\n' + '='*15 + ' Req No. 4 Answer ' + '='*15)
        print("Attemps between '" + initialDate + "' and '" + finalDate + "'")
        print("Total records: " + str(details['totalRecords']))
        print('\n' + '-'*6 + " Video Games release details " + '-'*6)
        print("There are '" + str(details['totalRecords']) + "' elements in range.")
        print('The first 3 and last 3 in range are:')
        headers = ['Record_Date_0', 'Count', 'Details']
        detailHeaders = ['Num_Runs', 'Time_0', 'Name', 'Players_0', 'Country_0', 'Platforms', 'Genres', 'Category', 'Subcategory', 'Release_Date']
        printTabulatedData(filtered, headers, detailHeaders)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 5:
        minTime = float(input('Minimum time of the interval: '))
        maxTime = float(input('Maximum time of the interval: '))
        startTime = controller.getTime()
        filtered, details = controller.getRegistersByRange(analyzer, minTime, maxTime)
        print('\n\n' + '='*15 + ' Req No. 5 Inputs ' + '='*15)
        print("Category records between '" + str(minTime) + "' and '" + str(maxTime) + "'")
        print('\n' + '='*15 + ' Req No. 5 Answer ' + '='*15)
        print("Attempts between '" + str(minTime) + "' and '" + str(maxTime) + "'")
        print("Total records: " + str(details["Number of records"]))
        print('\n' + '-'*7 + ' Videogame release details ' + '-'*7)
        print("There are '" + str(details["Number of elements"]) + "' elements in range")
        print("The first 3 and last 3 in range are: ")
        filtered = controller.firstAndLastThreeData(filtered)
        headers = ["Time_0", "Count", "Details"]
        detailHeaders = ['Record_Date_0', 'Num_Runs', 'Name', 'Players_0', 'Country_0', 'Platforms', 'Genres', 'Category', 'Subcategory', 'Release_Date']
        printTabulatedData(filtered, headers, detailHeaders)        
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 6:
        initialYear = int(input('Initial Year: '))
        finalYear = int(input('Final Year: '))
        print('\nChoose a feature for the Historigram\n')
        print('1- Best Time')
        print('2- Second Best Time')
        print('3- Third Best Time')
        print('4- Average Time')
        print('5- Number Runs')
        feature = input('\nFeature: ')
        numberSegments = int(input('Number Segents: '))
        numberLevels = int(input('Number Levels: '))
        feature = convertFeature(feature)
        startTime = controller.getTime()
        filtered, details = controller.histogramByReleaseYears(analyzer, initialYear, finalYear, feature, numberSegments, numberLevels)
        print('\n\n' + '='*15 + ' Req No. 6 Inputs ' + '='*15)
        print("Count map (histogram) of the feature: '" + feature + "'")
        print("Data between release years of '" + str(initialYear) + "' and '" + str(finalYear) + "'")
        print('Numbers of bins: ' + str(numberSegments))
        print('Registered attemps per scale: ' + str(numberLevels))
        print('\n' + '='*15 + ' Req No. 6 Answer ' + '='*15)
        print("There are '" + str(details['consultedAttemps']) + "' attemps on record.")
        print("Lowest value: '" + str(details['lowest']) + "'")
        print("Highest value: '" + str(details['highest']) + "'")
        print("The histogram counts '" + str(details['includedRegisters']) + "' attemps.")
        print("\n'" + feature + "' Histogram with '" + str(numberSegments) + "' bins and '" + str(numberLevels) + "' attemps per mark lvl.")
        headers = ['bin', 'count', 'lvl', 'mark']
        printTabulatedData(filtered, headers)
        print("NOTE: Each '*' reppresents " + str(numberLevels) + " attemps.\n")
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 7:
        platform = input('Platform: ')
        N = int(input('Top N: '))
        startTime = controller.getTime()
        filtered, details = controller.getTopNByProfitableVideogamesInPlatform(analyzer, platform, N)
        print('\n\n' + '='*15 + ' Req No. 7 Inputs ' + '='*15)
        print("Find the TOP '" + str(N) + "' games for '" + platform + "' platform.")
        print('\nFiltering record by platform...')
        print('Removing miscelaneous streaming revenue...')
        print('\n' + '='*15 + ' Req No. 7 Answer ' + '='*15)
        print("There are '" + str(details['registersInRange']) + "' records for '" + platform + "'.")
        print("There are '" + str(details['gamesByPlatform']) + "' available games in '" + platform + "'.")
        print('\n' + '-'*6 + " TOP " + str(N) + " GAMES FOR " + platform.upper() + " " + '-'*6)
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        headers = ['Rank', 'Name', 'Release_Date', 'Platforms', 'Genres', 'Stream_Revenue', 'Market_Share', 'Time_Avg', 'Total_Runs']
        printTabulatedData(filtered, headers)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)

    elif int(inputs[0]) == 8:
        year = int(input('Year: '))
        timeInf = float(input('Límite inferior de tiempo: '))
        timeSup = float(input('Límite superior de tiempo: '))
        startTime = controller.getTime()
        filtered, details = controller.graphAttempsByCountriesInRangeOfYears(analyzer, year, timeInf, timeSup)
        print('\n\n' + '='*15 + ' Req No. 8 (BONUS) Inputs ' + '='*15)
        print("Nationalities for best times in games released in '" + str(year) + "' in a range of times.")
        print("Range of times between '" + str(timeInf) + "' and '" + str(timeSup) + "' seconds.")
        print('\n' + '='*15 + ' Req No. 8 (BONUS) Answer ' + '='*15)
        print("There are '" + str(details['registersInRange']) + "' players with records between '" + str(timeInf) + "' and '" + str(timeSup) + "' seconds for games released in '" + str(year) + "'.")
        print('\n' + '-'*7 + " Countries' records details " + '-'*7)
        print("There are '" + str(lt.size(filtered)) + "' elements in range.")
        print("The first 3 and last 3 in range are: ")
        filtered = controller.firstAndLastThreeData(filtered)
        headers = ['Country', 'Count', 'Details']
        detailHeaders = ['Time_0', 'Players_0', 'Name', 'Release_Date']
        printTabulatedData(filtered, headers, detailHeaders)
        endTime = controller.getTime()
        deltaTime = str(round(controller.deltaTime(endTime, startTime), 2)) + " ms"
        print("Tiempo de ejecución: ", deltaTime)
        if details['Map'] is not None:
            print('\nDo you want to watch the Map?')
            print('\n1- Yes\n2- No')
            answer = input('\nAnswer: ')
            answer = convertAnswer(answer)
            if answer:
                webbrowser.open_new_tab('Map.html')

    else:
        sys.exit(0)

    input('\nPulse cualquier tecla para continuar...\n\n')   

sys.exit(0)
