import math
import sys
from PySide2 import QtCore, QtGui, QtWidgets

from polygonmisc import rotatePolygon, translatePolygon


class Human(QtWidgets.QGraphicsItem):
    BoundingRect = QtCore.QRectF(-20, -10, 40, 20)
    
    def __init__(self, id, xPos, yPos, angle):
        super(Human, self).__init__()
        self.id = id
        self.xPos = xPos
        self.yPos = yPos
        self.setAngle(angle)
        self.setPos(self.xPos, self.yPos)
        self.setZValue(1)
        self.colour = QtCore.Qt.transparent 
        self.pixmap = QtGui.QPixmap("person.png")

    @classmethod
    def from_json(Human, json_data):
        id = json_data['id']
        xPos = json_data['xPos']
        yPos = json_data['yPos']
        angle = json_data['orientation']
        return Human(id, xPos, yPos, angle)

    def setAngle(self, a):
        self.angle = a
        if self.angle > 180.:
            self.angle = -360.+self.angle
        self.setRotation(self.angle)

    def boundingRect(self):
        return Human.BoundingRect

    def polygon(self):
        w = 20
        h = 10
        polygon = QtGui.QPolygonF()
        polygon.append( QtCore.QPointF(-w, -h) )
        polygon.append( QtCore.QPointF(-w, +h) )
        polygon.append( QtCore.QPointF(+w, +h) )
        polygon.append( QtCore.QPointF(+w, -h) )
        polygon.append( QtCore.QPointF(-w, -h) )
        polygon = rotatePolygon(polygon, theta=self.angle*math.pi/180.)
        polygon = translatePolygon(polygon, tx=self.xPos, ty=self.yPos)
        return polygon

    def paint(self, painter, option, widget):
        painter.drawPixmap(self.BoundingRect.toRect(), self.pixmap)


