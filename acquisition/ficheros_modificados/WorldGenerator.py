import random
import math
import json
import time
import numpy as np

from PySide2 import QtCore, QtGui, QtWidgets

from human import Human
from robot import Robot
from regularobject import RegularObject
from room import Room
from interaction import Interaction

from collections import defaultdict
from scipy.spatial import distance

MAX_GENERATION_WAIT = 1.

class WorldGenerator(QtWidgets.QGraphicsScene):
    available_identifier = 0

    def __init__(self, data = None):
        super(WorldGenerator, self).__init__()
        self.setSceneRect(-400, -400, 800 - 2, 800 - 2)
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
    
        if data is None:
            self.generateRandomWorld()
        else:
            self.generateFromData(data)

    def generateFromData(self, raw_data):
        data = json.loads(raw_data)
        idMap = dict()
        self.clear()

        self.ds_identifier = int(data['identifier'].split()[0])

        self.room = Room(data['room'])
        self.addItem(self.room)

        self.humans = []
        for raw_human in data['humans']:
            human = Human.from_json(raw_human)
            self.addItem(human)
            self.humans.append(human)
            idMap[raw_human['id']] = human

        self.objects = []
        for raw_object in data['objects']:
            obj = RegularObject.from_json(raw_object)
            self.addItem(obj)
            self.objects.append(obj)
            idMap[raw_object['id']] = obj

        self.interactions = []
        interactions_done = []
        for interaction_raw in data['links']:
            if not [interaction_raw[1], interaction_raw[0], interaction_raw[2]] in interactions_done:
                interactions_done.append(interaction_raw)
                human = idMap[interaction_raw[0]]
                other = idMap[interaction_raw[1]]
                interaction = Interaction(human, other)
                self.interactions.append(interaction)
                self.addItem(interaction)


        self.robot = Robot()
        self.robot.setPos(0, 0)
        #self.addItem(self.robot)

    def generateRandomWorld(self):
        done = False
        self.ds_identifier = WorldGenerator.available_identifier
        WorldGenerator.available_identifier += 1
        while not done:
            try:
                self.generation_time = time.time()
                self.generate() #self.generate()
                done = True
                # print(time.time()-self.generation_time)
            except RuntimeError:
                pass

    @staticmethod
    def distanceTo(something):
        return int(math.sqrt(something.xPos*something.xPos + something.yPos*something.yPos))

    @staticmethod
    def angleTo(something):
        angle = int(int(180.*math.atan2(something.yPos, something.xPos)/math.pi)+90.)
        if angle > 180.: angle = -360.+angle
        return angle

    def serialize(self, score=-1):
        structure = dict()
        structure['identifier'] = str(self.ds_identifier).zfill(5) + ' A' # To change the identifier
        structure['score'] = 0
        if score > 0:
            structure['score'] = score
        structure['robot'] = {'id': 0}

        humansList = []
        for human in self.humans:
            h = dict()
            h['id'] = human.id
            h['xPos'] = +human.xPos
            h['yPos'] = +human.yPos
            h['orientation'] = +human.angle
            humansList.append(h)
        structure['humans'] = humansList

        objectsList = []
        for object in self.objects:
            o = dict()
            o['id'] = object.id
            o['xPos'] = +object.xPos
            o['yPos'] = +object.yPos
            o['orientation'] = +object.angle
            objectsList.append(o)
        structure['objects'] = objectsList

        structure['links'] = []
        for interaction in self.interactions:
            structure['links'].append( [interaction.a.id, interaction.b.id, 'interact'] )
            if type(interaction.b) is Human:
                structure['links'].append( [interaction.b.id, interaction.a.id, 'interact'] )

        structure['room'] = [ [+point.x(), point.y()] for point in self.room.poly ]

        if score >= 0:
            print(json.dumps(structure))

        return structure

    def generateHuman(self, availableId):
        human = None
        while human is None:
            if time.time() - self.generation_time > MAX_GENERATION_WAIT:
                raise RuntimeError('MAX_GENERATION_ATTEMPTS')
            if QtCore.qrand() % 3 == 0:
                xx = int(random.uniform(-215,215))
                yy = int(random.uniform(-215,215))
                
            else:
                xx = QtCore.qrand()%400-200
                yy = QtCore.qrand()%400-200
            human = Human(availableId, xx, yy, (QtCore.qrand()%360)-180)
            if not self.room.containsPolygon(human.polygon()):
                human = None
        return human

    def generateComplementaryHuman(self, human, availableId):
        a = math.pi*human.angle/180.
        #dist = float(QtCore.qrand()%300+50)
        dist = int(random.uniform(65, 225))
        xa = int(random.uniform(0,10))
        human2 = None
        while human2 is None:
            if time.time() - self.generation_time > MAX_GENERATION_WAIT:
                raise RuntimeError('MAX_GENERATION_ATTEMPTS')
            if (xa == 9 or xa == 8): # Generación totalmente aleatoria
                xPos = QtCore.qrand()%400-200
                yPos = QtCore.qrand()%400-200
                human2 = Human(availableId,xPos,yPos,(QtCore.qrand()%360)-180)
            else:
                xPos = (human.xPos+dist*math.sin(a))
                yPos = (human.yPos-dist*math.cos(a))
                c = human.angle + 180
                c_1 = (human.angle + 180)+60 # Amplitud de 60
                c_2 = (human.angle + 180)-60 # Amplitud de 60
                d = int(random.uniform(c_1, c_2))
                human2 = Human(availableId,xPos,yPos,d)
            if not self.room.containsPolygon(human2.polygon()):
                dist -= 30
                if dist < 30:
                    human.setAngle(human.angle+180)
                    a = math.pi*human.angle/180.
                    dist = float(random.uniform(55,65))
                    #dist = float(QtCore.qrand()%300+50)
                human2 = None
        return human2

    def generateComplementaryObject(self, human, availableId):
        a = math.pi*human.angle/180.
        dist = float(QtCore.qrand()%250+50)
        obj = None
        while obj is None:
            if time.time() - self.generation_time > MAX_GENERATION_WAIT:
                raise RuntimeError('MAX_GENERATION_ATTEMPTS')
            xPos = human.xPos+dist*math.sin(a)
            yPos = human.yPos-dist*math.cos(a)
            obj = RegularObject(availableId, xPos, yPos, (human.angle+180)%360)
            if not self.room.containsPolygon(obj.polygon()):
                dist -= 5
                if dist <= 5:
                    obj.setAngle(human.angle+180)
                    a = math.pi*human.angle/180.
                    dist = float(QtCore.qrand()%300+50)
                obj = None
        return obj
        

    def generate(self):
        regenerateScene = True
        while regenerateScene:

            availableId = 1
            regenerateScene = False
            self.clear()
            self.humans = []
            self.objects = []
            self.interactions = []

            self.room = Room()
            self.addItem(self.room)

            # We generate a number of humans using the absolute of a normal
            # variate with mean 1, sigma 4, capped to 15. If it's 15 we get
            # the remainder of /15

            humanCount = 1
            #humanCount = int(abs(random.normalvariate(1, 4))) % 15

            # Codigo original
            """if humanCount == 0:
                humanCount = QtCore.qrand() % 3"""

            for i in range(humanCount):
                human = self.generateHuman(availableId)
                availableId += 1
                self.addItem(human)
                self.humans.append(human)

                if humanCount == 1:
                    human2 = self.generateComplementaryHuman(human, availableId)
                    availableId += 1
                    self.addItem(human2)
                    self.humans.append(human2)
            
                # Codigo original    
                """if QtCore.qrand()%3 == 0:
                    human2 = self.generateComplementaryHuman(human, availableId)
                    availableId += 1
                    self.addItem(human2)
                    interaction = Interaction(human, human2)
                    self.interactions.append(interaction)
                    self.addItem(interaction)
                    self.humans.append(human2)
                elif QtCore.qrand()%2 == 0:
                    obj = self.generateComplementaryObject(human, availableId)
                    availableId += 1
                    interaction = Interaction(human, obj)
                    self.interactions.append(interaction)
                    self.addItem(interaction)
                    self.addItem(obj)
                    self.objects.append(obj)"""
            
            # Calculamos el punto medio de los dos humanos.
            x1 = human.xPos
            y1 = human.yPos
            x2 = human2.xPos
            y2 = human2.yPos
            x_pm = (x1 + x2)/2 
            y_pm = (y1 + y2)/2
            hum = (x_pm, y_pm)
            
            punto_medio = QtCore.QPointF(x_pm, y_pm) # Coordenada x e y del punto medio.
            punto_human = QtCore.QPointF(x1, y1) # Coordenada humano 1
            punto_human2 = QtCore.QPointF(x2, y2) # Coordenada humano 2.

            # Calcula las pendientes de las rectas que forman el escenario.
            puntos =  [ [+point.x(), point.y()] for point in self.room.poly ]
            #print(puntos) # Te muestra los puntos que componen la habitacion.
            puntos_lista = []

            for p in range(len(puntos)):
                for j in range(len(puntos[p])):
                    puntos_lista.append(puntos[p][j])
            #print(puntos_lista) # Te muestra una sola lista con todos los puntos por orden de aparición respetando la posición x e y.
            lista_x = puntos_lista[::2]
            #print(lista_x) # Divide "puntos_lista" y solo aparece las posiciones correspondientes a x
            lista_y = puntos_lista[1::2]
            #print(lista_y) # Divide "puntos_lista" y solo aparece las posiciones correspondientes a y

            resta_x = []
            resta_y = []
            for k in range(len(lista_x)-1):
                resta_x.append(lista_x[k+1]-lista_x[k])
            #print(resta_x) # Lista que contiene el resultado de restar el posterior al anterior (posiciones del eje x)
            for l in range(len(lista_y)-1):
                resta_y.append(lista_y[l+1]-lista_y[l])
            #print(resta_y) # Lista que contiene el resultado de restar el posterior al anterior (posiciones del eje y)

            try:
                valor_pendiente = [int(punto_y)/int(punto_x) for punto_y, punto_x in zip(resta_y,resta_x)]
            except ZeroDivisionError:
                break
            #print(valor_pendiente)
            
            # Nos muestra los valores que se repiten (rectas paralelas) y sus indices.
            aux = defaultdict(list)
            for index, item in enumerate(valor_pendiente):
                aux[item].append(index)
            result = {item: indexs for item, indexs in aux.items() if len(indexs) > 1}

            # Convertir el diccionario en listas sin bucle for.
            indices = list(result.keys()) # Valor de la pendiente.
            posiciones = list(result.values())# Veces que se repite cada valor de la pendiente.
            #print(indices) # Valor de la pendiente
            #print(posiciones) # Segmentos que indican que son paralelos segun el calculo de la pendiente.

            # Variables auxiliares.
            listas = []
            distPuntos = [] # Distancia entre punto inicial y punto final de un segmento.
            distPM_P1 = [] # Distancia entre el punto inicial de un segmento y el punto medio de las dos personas.
            distPM_P2 = [] # Distancia entre el punto final de un segmento y el punto medio de las dos personas.
            longitud_lista = []
            lmod = [] # Guarda los puntos cuyos segmentos formantes son paralelos.

            aux = []    
            listaComp = [] # Lista que recoge los resultados de la comparación. "1" indica que el punto medio esta entre los puntos inicio y final, "0" lo contrario.
            laux = []

            contador = 0
            cont = 0

            for m in range(len(posiciones)):
                for h in range(len(posiciones[m])):
                    contador = contador +1

            if ((len(posiciones) <= 3) and (contador == 2 or contador == 4 or contador == 6)):
                for m in range(len(posiciones)):
                    for h in range(len(posiciones[m])):
                        auxiliar = posiciones[m][h]
                        listas = [puntos[auxiliar], puntos[auxiliar+1]]
                        lmod.append(listas)

                        distancia_entreVertice = distance.euclidean(puntos[auxiliar], puntos[auxiliar+1]) # Calcula la distancia existente entre el punto inicial y punto final.
                        distPuntos.append(distancia_entreVertice)

                        distanciaPM_P1 = distance.euclidean(hum, puntos[auxiliar]) # Calcula la distancia entre el punto medio de las personas y el punto inicial del segmento.
                        distPM_P1.append(distanciaPM_P1)
                    
                        distanciaPM_P2 = distance.euclidean(hum, puntos[auxiliar+1]) # Calcula la distancia entre el punto medio de las personas y el punto final del segmento.
                        distPM_P2.append(distanciaPM_P2)

                        x = len(distPM_P2) # Para saber la longitud de las listas anteriores.
                        if x > 0:
                            longitud_lista = np.arange(x)

                #print(distPuntos) # Las distintas hipotenusas.
                #print(distPM_P1) # El primer punto
                #print(distPM_P2) # El segundo punto.
                
                for v in range(len(longitud_lista)):
                    aux.append(longitud_lista[v])

                # Comparación para ver si el punto medio esta entre punto inicial y final de los segmentos que son paralelos.
                for c in range(len(aux)):
                    if ((distPuntos[c]**2 + distPM_P1[c]**2 >= distPM_P2[c]**2 and distPuntos[c]**2 + distPM_P2[c]**2 >= distPM_P1[c]**2)):
                        listaComp.append(1)
                    else:
                        listaComp.append(0)
                #print(listaComp)

                # Transformación.
                for mi in range(len(lmod)):
                    for hi in range(len(lmod[mi])):
                        auxi = lmod[mi][hi]
                        laux.append(auxi)
                #print(laux)
                        
                # Asignación de puntos según las condiciones.
                for ti in range(len(listaComp)):
                    cont = cont +1
                    if cont == 0:
                        break
                    elif (cont == 2):
                        if (listaComp[0] == 1 and listaComp[1] == 1):

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[0]**2 - distPM_P1[0]**2 - distPuntos[0]**2) / (-2 * distPM_P1[0] * distPuntos[0]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A)
                            anguloA = cosA * (180 / math.pi)
                            #print(anguloA)

                            B = (distPM_P1[0]**2 - distPM_P2[0]**2 - distPuntos[0]**2) / (-2 * distPM_P2[0] * distPuntos[0]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B)
                            anguloB = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C = (distPuntos[0]**2 - distPM_P2[0]**2 - distPM_P1[0]**2) / (-2 * distPM_P2[0] * distPM_P1[0]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C)
                            anguloC = cosC * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo = anguloC + anguloB + anguloA # Suma de angulos = 180
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA = math.radians(anguloA)
                            m = distPM_P1[0] * math.cos(angA)

                            angB = math.radians(anguloB)
                            n = distPM_P2[0] * math.cos(angB)

                            segmentoC = m + n # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[0])

                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[0][0] + (razon * laux[1][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[0][1] + (razon * laux[1][1])) / (1 + razon)) # Punto Y de la intersección.

                            punto_Segmento1 = QtCore.QPointF(X,Y) # Asignación a la estructura de qt el primer punto.
                            print(punto_Segmento1)

                            """##### Segundo Segmento #####
                            ############################"""
                
                            A_2 = (distPM_P2[1]**2 - distPM_P1[1]**2 - distPuntos[1]**2) / (-2 * distPM_P1[1] * distPuntos[1]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A_2)
                            anguloA_2 = cosA_2 * (180 / math.pi)
                            #print(anguloA_2)

                            B_2 = (distPM_P1[1]**2 - distPM_P2[1]**2 - distPuntos[1]**2) / (-2 * distPM_P2[1] * distPuntos[1]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B_2)
                            anguloB_2 = cosB_2 * (180 / math.pi)
                            #print(anguloB_2)
                
                            C_2 = (distPuntos[1]**2 - distPM_P2[1]**2 - distPM_P1[1]**2) / (-2 * distPM_P2[1] * distPM_P1[1]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2)
                            anguloC_2 = cosC_2 * (180 / math.pi)
                            #print(anguloC_2)
                            
                            sumaAngulo_2 = anguloC_2 + anguloB_2 + anguloA_2
                            #print(sumaAngulo_2) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA_2 = math.radians(anguloA_2)
                            m_2 = distPM_P1[1] * math.cos(angA_2)

                            angB_2 = math.radians(anguloB_2)
                            n_2 = distPM_P2[1] * math.cos(angB_2)

                            segmentoC_2 = m_2 + n_2 # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC_2)
                            #print(distPuntos[1])

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[2][0] + (razon_2 * laux[3][0])) / (1 + razon_2)) # Punto X de la segunda intersección.
                            Y_2 = ((laux[2][1] + (razon_2 * laux[3][1])) / (1 + razon_2)) # Punto Y de la segunda intersección.

                            punto_Segmento2 = QtCore.QPointF(X_2, Y_2) # Asignación a la estructura de qt el segundo punto.
                            print(punto_Segmento2)

                            lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2)
                            print(lineaNuevaPared)

                            punto_medio = QtCore.QPointF(x_pm, y_pm)
                            print(punto_medio)
                            
                            break
                        
                    elif (cont == 4):
                        if (listaComp[0] == 1 and listaComp[1] == 1):

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[0]**2 - distPM_P1[0]**2 - distPuntos[0]**2) / (-2 * distPM_P1[0] * distPuntos[0]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A)
                            anguloA = cosA * (180 / math.pi)
                            #print(anguloA)

                            B = (distPM_P1[0]**2 - distPM_P2[0]**2 - distPuntos[0]**2) / (-2 * distPM_P2[0] * distPuntos[0]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B)
                            anguloB = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C = (distPuntos[0]**2 - distPM_P2[0]**2 - distPM_P1[0]**2) / (-2 * distPM_P2[0] * distPM_P1[0]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C)
                            anguloC = cosC * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo = anguloC + anguloB + anguloA
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A.
                            angA = math.radians(anguloA)
                            m = distPM_P1[0] * math.cos(angA)

                            angB = math.radians(anguloB)
                            n = distPM_P2[0] * math.cos(angB)

                            segmentoC = m + n # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[0])

                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[0][0] + (razon * laux[1][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[0][1] + (razon * laux[1][1])) / (1 + razon)) # Punto Y de la intersección.

                            punto_Segmento1 = QtCore.QPointF(X,Y)
                            print(punto_Segmento1)

                            ##### Segundo Segmento #####
                            ############################
                
                            A_2 = (distPM_P2[1]**2 - distPM_P1[1]**2 - distPuntos[1]**2) / (-2 * distPM_P1[1] * distPuntos[1]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A_2)
                            anguloA_2 = cosA_2 * (180 / math.pi)
                            #print(anguloA_2)

                            B_2 = (distPM_P1[1]**2 - distPM_P2[1]**2 - distPuntos[1]**2) / (-2 * distPM_P2[1] * distPuntos[1]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B_2)
                            anguloB_2 = cosB_2 * (180 / math.pi)
                            #print(anguloB_2)
                
                            C_2 = (distPuntos[1]**2 - distPM_P2[1]**2 - distPM_P1[1]**2) / (-2 * distPM_P2[1] * distPM_P1[1]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2)
                            anguloC_2 = cosC_2 * (180 / math.pi)
                            #print(anguloC_2)

                            sumaAngulo_2 = anguloC_2 + anguloB_2 + anguloA_2
                            #print(sumaAngulo_2) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA_2 = math.radians(anguloA_2)
                            m_2 = distPM_P1[1] * math.cos(angA_2)

                            angB_2 = math.radians(anguloB_2)
                            n_2 = distPM_P2[1] * math.cos(angB_2)

                            segmentoC_2 = m_2 + n_2 # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC_2)
                            #print(distPuntos[1])

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[2][0] + (razon_2 * laux[3][0])) / (1 + razon_2)) # Punto X de la segunda intersección.
                            Y_2 = ((laux[2][1] + (razon_2 * laux[3][1])) / (1 + razon_2)) # Punto Y de la segunda intersección.

                            punto_Segmento2 = QtCore.QPointF(X_2, Y_2)
                            print(punto_Segmento2)

                            lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2)
                            print(lineaNuevaPared)

                            punto_medio = QtCore.QPointF(x_pm, y_pm)
                            print(punto_medio)

                            break
                                                        
                        elif (listaComp[2] == 1 and listaComp[3] == 1):

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[2]**2 - distPM_P1[2]**2 - distPuntos[2]**2) / (-2 * distPM_P1[2] * distPuntos[2]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A)
                            anguloA = cosA * (180 / math.pi)
                            #print(anguloA)

                            B = (distPM_P1[2]**2 - distPM_P2[2]**2 - distPuntos[2]**2) / (-2 * distPM_P2[2] * distPuntos[2]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B)
                            anguloB = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C = (distPuntos[2]**2 - distPM_P2[2]**2 - distPM_P1[2]**2) / (-2 * distPM_P2[2] * distPM_P1[2]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C)
                            anguloC = cosC * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo = anguloC + anguloB + anguloA
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A.
                            angA = math.radians(anguloA)
                            m = distPM_P1[2] * math.cos(angA)

                            angB = math.radians(anguloB)
                            n = distPM_P2[2] * math.cos(angB)

                            segmentoC = m + n # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[2])

                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[4][0] + (razon * laux[5][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[4][1] + (razon * laux[5][1])) / (1 + razon)) # Punto Y de la intersección.

                            punto_Segmento1 = QtCore.QPointF(X,Y)
                            print(punto_Segmento1)

                            ##### Segundo Segmento #####
                            ############################
                
                            A_2 = (distPM_P2[3]**2 - distPM_P1[3]**2 - distPuntos[3]**2) / (-2 * distPM_P1[3] * distPuntos[3]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A_2)
                            anguloA_2 = cosA_2 * (180 / math.pi)
                            #print(anguloA_2)

                            B_2 = (distPM_P1[3]**2 - distPM_P2[3]**2 - distPuntos[3]**2) / (-2 * distPM_P2[3] * distPuntos[3]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B_2)
                            anguloB_2 = cosB_2 * (180 / math.pi)
                            #print(anguloB_2)
                
                            C_2 = (distPuntos[3]**2 - distPM_P2[3]**2 - distPM_P1[3]**2) / (-2 * distPM_P2[3] * distPM_P1[3]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2)
                            anguloC_2 = cosC_2 * (180 / math.pi)
                            #print(anguloC_2)

                            sumaAngulo_2 = anguloC_2 + anguloB_2 + anguloA_2
                            #print(sumaAngulo_2) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA_2 = math.radians(anguloA_2)
                            m_2 = distPM_P1[3] * math.cos(angA_2)

                            angB_2 = math.radians(anguloB_2)
                            n_2 = distPM_P2[3] * math.cos(angB_2)

                            segmentoC_2 = m_2 + n_2 # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC_2)
                            #print(distPuntos[3])

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[6][0] + (razon_2 * laux[7][0])) / (1 + razon_2)) # Punto X de la segunda intersección.
                            Y_2 = ((laux[6][1] + (razon_2 * laux[7][1])) / (1 + razon_2)) # Punto Y de la segunda intersección.

                            punto_Segmento2 = QtCore.QPointF(X_2, Y_2)
                            print(punto_Segmento2)

                            lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2)
                            print(lineaNuevaPared)

                            punto_medio = QtCore.QPointF(x_pm, y_pm)
                            print(punto_medio)

                            break

                    elif (cont == 6):
                        if (listaComp[0] == 1 and listaComp[1] == 1):

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[0]**2 - distPM_P1[0]**2 - distPuntos[0]**2) / (-2 * distPM_P1[0] * distPuntos[0]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A)
                            anguloA = cosA * (180 / math.pi)
                            #print(anguloA)

                            B = (distPM_P1[0]**2 - distPM_P2[0]**2 - distPuntos[0]**2) / (-2 * distPM_P2[0] * distPuntos[0]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B)
                            anguloB = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C = (distPuntos[0]**2 - distPM_P2[0]**2 - distPM_P1[0]**2) / (-2 * distPM_P2[0] * distPM_P1[0]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C)
                            anguloC = cosC * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo = anguloC + anguloB + anguloA
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A.
                            angA = math.radians(anguloA)
                            m = distPM_P1[0] * math.cos(angA)

                            angB = math.radians(anguloB)
                            n = distPM_P2[0] * math.cos(angB)

                            segmentoC = m + n # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[0])

                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[0][0] + (razon * laux[1][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[0][1] + (razon * laux[1][1])) / (1 + razon)) # Punto Y de la intersección.

                            punto_Segmento1 = QtCore.QPointF(X,Y)
                            print(punto_Segmento1)

                            ##### Segundo Segmento #####
                            ############################
                
                            A_2 = (distPM_P2[1]**2 - distPM_P1[1]**2 - distPuntos[1]**2) / (-2 * distPM_P1[1] * distPuntos[1]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A_2)
                            anguloA_2 = cosA_2 * (180 / math.pi)
                            #print(anguloA_2)

                            B_2 = (distPM_P1[1]**2 - distPM_P2[1]**2 - distPuntos[1]**2) / (-2 * distPM_P2[1] * distPuntos[1]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B_2)
                            anguloB_2 = cosB_2 * (180 / math.pi)
                            #print(anguloB_2)
                
                            C_2 = (distPuntos[1]**2 - distPM_P2[1]**2 - distPM_P1[1]**2) / (-2 * distPM_P2[1] * distPM_P1[1]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2)
                            anguloC_2 = cosC_2 * (180 / math.pi)
                            #print(anguloC_2)

                            sumaAngulo_2 = anguloC_2 + anguloB_2 + anguloA_2
                            #print(sumaAngulo_2) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA_2 = math.radians(anguloA_2)
                            m_2 = distPM_P1[1] * math.cos(angA_2)

                            angB_2 = math.radians(anguloB_2)
                            n_2 = distPM_P2[1] * math.cos(angB_2)

                            segmentoC_2 = m_2 + n_2 # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC_2)
                            #print(distPuntos[1])

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[2][0] + (razon_2 * laux[3][0])) / (1 + razon_2)) # Punto X de la segunda intersección.
                            Y_2 = ((laux[2][1] + (razon_2 * laux[3][1])) / (1 + razon_2)) # Punto Y de la segunda intersección.

                            punto_Segmento2 = QtCore.QPointF(X_2, Y_2)
                            print(punto_Segmento2)

                            lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2)
                            print(lineaNuevaPared)

                            punto_medio = QtCore.QPointF(x_pm, y_pm)
                            print(punto_medio)

                        elif (listaComp[2] == 1 and listaComp[3] == 1):
                            
                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[2]**2 - distPM_P1[2]**2 - distPuntos[2]**2) / (-2 * distPM_P1[2] * distPuntos[2]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A)
                            anguloA = cosA * (180 / math.pi)
                            #print(anguloA)

                            B = (distPM_P1[2]**2 - distPM_P2[2]**2 - distPuntos[2]**2) / (-2 * distPM_P2[2] * distPuntos[2]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B)
                            anguloB = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C = (distPuntos[2]**2 - distPM_P2[2]**2 - distPM_P1[2]**2) / (-2 * distPM_P2[2] * distPM_P1[2]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C)
                            anguloC = cosC * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo = anguloC + anguloB + anguloA
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A.
                            angA = math.radians(anguloA)
                            m = distPM_P1[2] * math.cos(angA)

                            angB = math.radians(anguloB)
                            n = distPM_P2[2] * math.cos(angB)

                            segmentoC = m + n # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[2])

                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[4][0] + (razon * laux[5][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[4][1] + (razon * laux[5][1])) / (1 + razon)) # Punto Y de la intersección.

                            punto_Segmento1 = QtCore.QPointF(X,Y)
                            print(punto_Segmento1)

                            ##### Segundo Segmento #####
                            ############################
                
                            A_2 = (distPM_P2[3]**2 - distPM_P1[3]**2 - distPuntos[3]**2) / (-2 * distPM_P1[3] * distPuntos[3]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A_2)
                            anguloA_2 = cosA_2 * (180 / math.pi)
                            #print(anguloA_2)

                            B_2 = (distPM_P1[3]**2 - distPM_P2[3]**2 - distPuntos[3]**2) / (-2 * distPM_P2[3] * distPuntos[3]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B_2)
                            anguloB_2 = cosB_2 * (180 / math.pi)
                            #print(anguloB_2)
                
                            C_2 = (distPuntos[3]**2 - distPM_P2[3]**2 - distPM_P1[3]**2) / (-2 * distPM_P2[3] * distPM_P1[3]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2)
                            anguloC_2 = cosC_2 * (180 / math.pi)
                            #print(anguloC_2)

                            sumaAngulo_2 = anguloC_2 + anguloB_2 + anguloA_2
                            #print(sumaAngulo_2) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A. n = segunda proyección. Sobre el angulo B.
                            angA_2 = math.radians(anguloA_2)
                            m_2 = distPM_P1[3] * math.cos(angA_2)

                            angB_2 = math.radians(anguloB_2)
                            n_2 = distPM_P2[3] * math.cos(angB_2)

                            segmentoC_2 = m_2 + n_2 # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC_2)
                            #print(distPuntos[3])

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[6][0] + (razon_2 * laux[7][0])) / (1 + razon_2)) # Punto X de la segunda intersección.
                            Y_2 = ((laux[6][1] + (razon_2 * laux[7][1])) / (1 + razon_2)) # Punto Y de la segunda intersección.

                            punto_Segmento2 = QtCore.QPointF(X_2, Y_2)
                            print(punto_Segmento2)

                            lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2)
                            print(lineaNuevaPared)

                            punto_medio = QtCore.QPointF(x_pm, y_pm)
                            print(punto_medio)

                        elif (listaComp[4] == 1 and listaComp[5] == 1):

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A = (distPM_P2[4]**2 - distPM_P1[4]**2 - distPuntos[4]**2) / (-2 * distPM_P1[4] * distPuntos[4]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA =math.acos(A)
                            anguloA = cosA * (180 / math.pi)
                            #print(anguloA)

                            B = (distPM_P1[4]**2 - distPM_P2[4]**2 - distPuntos[4]**2) / (-2 * distPM_P2[4] * distPuntos[4]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB = math.acos(B)
                            anguloB = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C = (distPuntos[4]**2 - distPM_P2[4]**2 - distPM_P1[4]**2) / (-2 * distPM_P2[4] * distPM_P1[4]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC = math.acos(C)
                            anguloC = cosC * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo = anguloC + anguloB + anguloA
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A.
                            angA = math.radians(anguloA)
                            m = distPM_P1[4] * math.cos(angA)

                            angB = math.radians(anguloB)
                            n = distPM_P2[4] * math.cos(angB)

                            segmentoC = m + n # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[4])

                            # Para averiguar el punto que divide a ese segmento.
                            razon = m / n # Razon entre segmentos
                            X = ((laux[8][0] + (razon * laux[9][0])) / (1 + razon)) # Punto X de la intersección.
                            Y = ((laux[8][1] + (razon * laux[9][1])) / (1 + razon)) # Punto Y de la intersección.

                            punto_Segmento1 = QtCore.QPointF(X,Y)
                            print(punto_Segmento1)

                            ##### Segundo Segmento #####
                            ############################

                            # Para averiguar los angulos del vercite primero y el vertice segundo.
                            A_2 = (distPM_P2[5]**2 - distPM_P1[5]**2 - distPuntos[5]**2) / (-2 * distPM_P1[5] * distPuntos[5]) # Angulo A (primer angulo formante) correspondiente al vertice del punto 1.
                            cosA_2 =math.acos(A)
                            anguloA_2 = cosA * (180 / math.pi)
                            #print(anguloA)

                            B_2 = (distPM_P1[5]**2 - distPM_P2[5]**2 - distPuntos[5]**2) / (-2 * distPM_P2[5] * distPuntos[5]) # Angulo B (segundo angulo formante) correspondiente al vertice del punto2.
                            cosB_2 = math.acos(B)
                            anguloB_2 = cosB * (180 / math.pi)
                            #print(anguloB)
                
                            C_2 = (distPuntos[5]**2 - distPM_P2[5]**2 - distPM_P1[5]**2) / (-2 * distPM_P2[5] * distPM_P1[5]) # Angulo C (tercer angulo formante) correspondiente al vertice del punto medio.
                            cosC_2 = math.acos(C_2)
                            anguloC_2 = cosC_2 * (180 / math.pi)
                            #print(anguloC)

                            sumaAngulo_2 = anguloC_2 + anguloB_2 + anguloA_2
                            #print(sumaAngulo) # Para comprobar si el triangulo cumple las condiciones que debe cumplir. (Suma de angulos = 180)

                
                            # Para averiguar la proyección existente entre las distancias que van de el punto medio hacia los distintos vertices. ( m = primera proyección, n = segunda proyeccion)
                            # m = primera proyección. Sobre el angulo A.
                            angA_2 = math.radians(anguloA_2)
                            m_2 = distPM_P1[5] * math.cos(angA_2)

                            angB_2 = math.radians(anguloB_2)
                            n_2 = distPM_P2[5] * math.cos(angB_2)

                            segmentoC_2 = m_2 + n_2 # Comprobación para saber si las dos proyecciones son iguales a la longitud total de la hipotenusa.
                            #print(segmentoC)
                            #print(distPuntos[5])

                            # Para averiguar el punto que divide a ese segmento.
                            razon_2 = m_2 / n_2 # Razon entre segmentos
                            X_2 = ((laux[10][0] + (razon_2 * laux[11][0])) / (1 + razon_2)) # Punto X de la intersección.
                            Y_2 = ((laux[10][1] + (razon_2 * laux[11][1])) / (1 + razon_2)) # Punto Y de la intersección.

                            punto_Segmento2 = QtCore.QPointF(X_2,Y_2)
                            print(punto_Segmento2)

                            lineaNuevaPared = QtCore.QLineF(punto_Segmento1, punto_Segmento2)
                            print(lineaNuevaPared)

                            punto_medio = QtCore.QPointF(x_pm, y_pm)
                            print(punto_medio)
                            
                                
            # Transformación de coordenadas rectangulares a coordenadas polares
            """for i in puntos:
                x = len(puntos)
                #print(x-1)
                if x > 0:
                    lista_vertices = np.arange(x)
                    #print(lista_vertices)
                    for j in lista_vertices:
                        k = 0
                        m = 1
                        coordenada1 = puntos[j][k]
                        coordenada2 = puntos[j][m]
                        x_dis = math.sqrt(coordenada1*coordenada1 + coordenada2*coordenada2)
                        x_ang = int(int(180.*math.atan2(coordenada2, coordenada1)/math.pi)+90.)
                        if x_ang > 180.:
                            x_ang = -360.+x_ang
                        coordenada_general = [x_dis, x_ang]
                        print(coordenada_general)
                    break"""

            
            # Dibujar: linea entre vertices, punto en la posición punto medio, dibujar linea que une los dos humanos.

            """#self.colour = QtCore.Qt.red
            #self.room.addLine(lineaNuevaPared, colour)
            #self.addItem(self.room)"""

            """# Dibujar un punto en el punto medio de los dos humanos.
            #self.room = Room()
            #self.room.drawPoint(x_pm,y_pm)
            #self.addItem(self.room)
            #self.room.drawPoint(x_pm,y_pm)
            #self.room.addLine(float(x1),float(y1),x2,y2,self.linea_color)
            #self.addItem(self.room)"""

                 
            self.robot = Robot()
            self.robot.setPos(0, 0)
            #self.addItem(self.robot)


        self.text = 'Humans:' + str(len(self.humans)) + ' ' + 'Objects:' + str(len(self.objects))

