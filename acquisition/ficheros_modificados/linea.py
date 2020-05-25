import math

from PySide2 import QtCore, QtGui, QtWidgets


class Linea(QtWidgets.QGraphicsItem):
    def __init__(self, a, b):
        super(Linea, self).__init__()
        self.a = a
        self.b = b
        
        self.xPos = (self.a.xPos + self.b.xPos) / 2
        self.yPos = (self.a.yPos + self.b.yPos) / 2

        s1 = self.a.xPos - self.b.xPos
        s2 = self.a.yPos - self.b.yPos
        d = math.sqrt(s1*s1 + s2*s2)
        angle = math.atan2(s2, s1)
        

        self.length = d # Distancia entre ellos
        self.setPos(self.xPos, self.yPos) # Punto medio
        self.BoundingRect = QtCore.QRectF(-d/2, 0, d, 0)
        self.setRotation(angle*180./math.pi)
        self.text = QtGui.QStaticText("dis")

        #self.punto1 = QtCore.QPointF(self.hum.xPos, self.hum.yPos) # Asignación punto1.
        #self.punto2 = QtCore.QPointF(self.hum2.xPos, self.hum2.yPos) # Asignación punto2.
        self.puntomedio = QtCore.QPointF(self.xPos, self.yPos) # Asignación punto medio.
        #self.lineaNueva = QtCore.QLineF(self.punto1, self.punto2) #Linea entre humano.
        
    def boundingRect(self):
        return self.BoundingRect


    def paint(self, painter, option, widget):
            if (self.length > 40):
                painter.drawRect(-self.length/2, 0, self.length, 0)
                painter.drawStaticText(self.puntomedio, self.text)

