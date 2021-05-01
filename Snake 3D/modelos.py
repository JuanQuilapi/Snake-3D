import basic_shapes as bs
import transformations as tr
from OpenGL.GL import *
import easy_shaders as es
import basic_shapes_extended as bs_ext
import scene_graph as sg
import random
import math
import numpy as np
class Fondo(object):
    def __init__(self):
        # figura base
        gpuBorde = es.toGPUShape(bs.createTextureCube("img/piedras2.png"), GL_REPEAT, GL_NEAREST)
        celdaB = sg.SceneGraphNode('celdaBorde')
        celdaB.transform = tr.uniformScale(1/20)
        celdaB.childs += [gpuBorde]
        gpuFondo = es.toGPUShape(bs.createTextureQuad("img/grass1.png"), GL_REPEAT, GL_NEAREST)
        celda = sg.SceneGraphNode('celda')
        celda.childs += [gpuFondo]

        def createCeldaBorde(x, y):
            newcelda = sg.SceneGraphNode('celdaBorde' + str(x) + str(y))
            newcelda.transform = tr.translate(1/20 * x, 1/20 * y, 0)
            newcelda.childs += [celdaB]
            return newcelda

        celdasxyBorde = []

        def createBorde(n):
            for i in range(n // 2, -n // 2-1, -1):
                for j in range(n // 2, -n // 2-1, -1):
                    if i == n // 2 or i == -n // 2 :
                        x = createCeldaBorde(i, j)
                        celdasxyBorde.append(x)
                    if j == n // 2 or j == -n // 2 :
                        x = createCeldaBorde(i, j)
                        celdasxyBorde.append(x)
            return celdasxyBorde

        createBorde(20)
        Borde = sg.SceneGraphNode('Borde')
        Borde.childs += celdasxyBorde
        grilla = sg.SceneGraphNode('grilla')
        grilla.childs = [celda]
        self.grilla = grilla
        self.Borde = Borde
        self.tamanoC =celdaB

    def draw(self, pipeline):
        self.grilla.transform = tr.matmul([tr.translate(0,0,-1/40),tr.uniformScale(1.9)])
        self.Borde.transform = tr.uniformScale(2)
        sg.drawSceneGraphNode(self.grilla, pipeline, 'model')
        sg.drawSceneGraphNode(self.Borde, pipeline, 'model')

class Snake(object):
    def __init__(self):
        # figura base
        gpuHead = es.toGPUShape(bs.createTextureCube("img/body1.png"), GL_REPEAT, GL_NEAREST)
        gpuBody = es.toGPUShape(bs.createTextureCube("img/body1.png"), GL_REPEAT, GL_NEAREST)
        # creamos la cabeza
        head = sg.SceneGraphNode('head')
        head.transform = tr.uniformScale(0.063)
        head.childs += [gpuHead]
        # creamos la rotacion de la cabeza
        transform_head = sg.SceneGraphNode('headTR')
        transform_head.childs += [head]
        self.head = transform_head
        # creamos el cuerpo
        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(0.05)
        body.childs += [gpuBody]
        transform_body = sg.SceneGraphNode('BodyTR')
        transform_body.childs += [body]

        def createBody(n):
            newBody = sg.SceneGraphNode('body' + str(n))
            newBody.transform = tr.matmul([tr.translate(0, 0, 0)])  # tr.matmul([])..
            newBody.childs += [body]
            transform_newBody = sg.SceneGraphNode('newBodyTR' + str(n))
            transform_newBody.childs += [newBody]
            return newBody

        Bodys = [createBody(1),createBody(2),createBody(3),createBody(4),createBody(5)]
        self.Bodys = Bodys
        posbX = [0, 0 ,0, 0, 0]
        directionsb = ['up', 'up', 'up', 'up', 'up']
        self.posbX = posbX
        self.o = 10
        posbY = [0, -1/20, -2/20, -3/20, -4/20]
        self.posbY = posbY
        self.direction = 'up'
        self.headS = head
        self.bodyS = body
        self.head = transform_head
        self.body = transform_body
        self.posX = 0
        self.posY = 0
        self.posUGiro = [0, 0]
        self.posDGiro = [0, 0]
        self.posRGiro = [0, 0]
        self.posLGiro = [0, 0]
        self.directionsb = directionsb
        self.n = 0
        self.createBody = createBody(self.n)
        self.collideW = False
        self.collideS = False
        self.rotate = 0
        self.stop = False
        self.bug = False
        self.bugCount = 0
    def draw(self, pipeline):
        self.head.transform = tr.matmul([tr.translate(self.posX, self.posY, 0), tr.rotationZ(self.rotate)])
        for i in range(len(self.Bodys)):
            x = self.posbX[i]
            y = self.posbY[i]
            if i ==0:
                self.Bodys[i].transform = tr.matmul([tr.translate(x, y, 0)])
            else:
                self.Bodys[i].transform = tr.translate(x, y, 0)
            sg.drawSceneGraphNode(self.Bodys[i], pipeline, 'model')
        sg.drawSceneGraphNode(self.head, pipeline, 'model')

    def alargar(self):
        n = len(self.Bodys)
        self.n = n + 1
        self.Bodys.append(self.createBody)
        self.directionsb.append(self.directionsb[n - 1])
        if self.directionsb[n] == 'up':
            self.posbX.append(self.posbX[n - 1])
            self.posbY.append(self.posbY[n - 1] - 1/20)
        if self.directionsb[n] == 'down':
            self.posbX.append(self.posbX[n - 1])
            self.posbY.append(self.posbY[n - 1] + 1/20)
        if self.directionsb[n] == 'right':
            self.posbX.append(self.posbX[n - 1] - 1/20)
            self.posbY.append(self.posbY[n - 1])
        if self.directionsb[n] == 'left':
            self.posbX.append(self.posbX[n - 1] + 1/20)
            self.posbY.append(self.posbY[n - 1])

    def Bug(self):
        distX = []
        distY = []
        for i in range(1,len(self.posbX)):
            x = abs(self.posbX[i] - self.posbX[i - 1])
            y = abs(self.posbY[i] - self.posbY[i - 1])
            distX.append(x)
            distY.append(y)
            if x> 0.06 or y>0.06:
                self.bug = True
            if self.bugCount >0:
                if x==0 or y==0:
                    self.bug = True
        #print("X= ", distX, "Y= ", distY)



    def Ibug(self):
        for i in range(1,len(self.posbX)):
            x = abs(self.posbX[i] - self.posbX[i - 1])
            y = abs(self.posbY[i] - self.posbY[i - 1])
            if x > 0.06 or y > 0.06:
                return i-1
    def fix(self,i):
        x = 0
        y = 0
        if self.directionsb[i] == 'up':
            x, y = 0, -1/20
        if self.directionsb[i] == 'down':
            x, y = 0, 1/20
        if self.directionsb[i] == 'left':
            x, y = 1/20, 0
        if self.directionsb[i] == 'left':
            x, y = -1/20, 0
        for i in range(i,len(self.posbX)):
            self.posbX[i] = self.posbX[i-1]+x
            self.posbY[i] = self.posbY[i-1]+y
    def restart(self):
        self.direction = 'up'
        self.posX = 0
        self.posY = 0
        self.posUGiro = [0, 0]
        self.posDGiro = [0, 0]
        self.posRGiro = [0, 0]
        self.posLGiro = [0, 0]
        for i in range(len(self.Bodys)):
            self.directionsb[i] = 'up'
            self.posbX[i] = 0
            self.posbY[i] = i*(-1/20)

    def collideWall(self):
        limit = 1-(1/20*1.55)
        if abs(self.posX - limit) < 0.001 or abs(self.posX + limit) < 0.001 or abs(self.posY - limit) < 0.001 or abs(
                self.posY + limit) < 0.001:
            self.collideW = True
            self.stop = True

    def collideSnake(self):
        for i in range(1,len(self.Bodys)):
            if abs(self.posbX[i]-self.posX)<0.01 and abs(self.posbY[i]-self.posY)<0.01:
                self.collideS = True
                self.stop = True

    def update(self, dt):
        dif = 0.002
        if self.direction == 'right':
            self.posX += dt
            self.directionsb[0] = 'right'
            self.posbX[0] += dt
        if self.direction == 'left':
            self.posX -= dt
            self.directionsb[0] = 'left'
            self.posbX[0] -= dt

        if self.direction == 'up':
            self.posY += dt
            self.directionsb[0] = 'up'
            self.posbY[0] += dt

        if self.direction == 'down':
            self.posY -= dt
            self.directionsb[0] = 'down'
            self.posbY[0] -= dt
        for i in range(1, len(self.Bodys)):
            if self.directionsb[i] == 'up' and abs(self.posbX[i] - self.posUGiro[1]) < dif:
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[1]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[0]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[1]) < dif:
                    self.directionsb[i] = 'left'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[0]) < dif:
                    self.directionsb[i] = 'left'
                if self.directionsb[i - 1] == 'down':
                    if self.posbX[i] < self.posbX[i - 1]:
                        if abs(self.posbY[i] - self.posRGiro[1]) < dif:
                            self.directionsb[i] = 'right'
                        else:
                            self.posbY[i] += dt
                    if self.posbX[i] > self.posbX[i - 1]:
                        if abs(self.posbY[i] - self.posLGiro[1]) < dif:
                            self.directionsb[i] = 'left'
                        else:
                            self.posbY[i] += dt
                else:
                    self.posbY[i] += dt
            elif self.directionsb[i] == 'up' and abs(self.posbX[i] - self.posUGiro[0]) < dif:
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[1]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[0]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[1]) < dif:
                    self.directionsb[i] = 'left'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[0]) < dif:
                    self.directionsb[i] = 'left'
                else:
                    self.posbY[i] += dt


            elif self.directionsb[i] == 'down' and abs(self.posbX[i] - self.posDGiro[1]) < dif:
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[1]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[0]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[1]) < dif:
                    self.directionsb[i] = 'left'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[0]) < dif:
                    self.directionsb[i] = 'left'
                if self.directionsb[i - 1] == 'up':
                    if self.posbX[i] < self.posbX[i - 1]:
                        if abs(self.posbY[i] - self.posRGiro[1]) < dif:
                            self.directionsb[i] = 'right'
                        else:
                            self.posbY[i] -= dt
                    if self.posbX[i] > self.posbX[i - 1]:
                        if abs(self.posbY[i] - self.posLGiro[1]) < dif:
                            self.directionsb[i] = 'left'
                        else:
                            self.posbY[i] -= dt
                else:
                    self.posbY[i] -= dt
            elif self.directionsb[i] == 'down' and abs(self.posbX[i] - self.posDGiro[0]) < dif:
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[1]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'right' and abs(self.posbY[i] - self.posRGiro[0]) < dif:
                    self.directionsb[i] = 'right'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[1]) < dif:
                    self.directionsb[i] = 'left'
                if self.directionsb[i - 1] == 'left' and abs(self.posbY[i] - self.posLGiro[0]) < dif:
                    self.directionsb[i] = 'left'
                else:
                    self.posbY[i] -= dt

            elif self.directionsb[i] == 'left' and abs(self.posbY[i] - self.posLGiro[1]) < dif:
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[1]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[0]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[1]) < dif:
                    self.directionsb[i] = 'down'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[0]) < dif:
                    self.directionsb[i] = 'down'
                if self.directionsb[i - 1] == 'right':
                    if self.posbY[i] < self.posbY[i - 1]:
                        if abs(self.posbX[i] - self.posUGiro[1]) < dif:
                            self.directionsb[i] = 'up'
                        else:
                            self.posbX[i] -= dt
                    if self.posbX[i] > self.posbX[i - 1]:
                        if abs(self.posbY[i] - self.posDGiro[1]) < dif:
                            self.directionsb[i] = 'down'
                        else:
                            self.posbX[i] -= dt
                else:
                    self.posbX[i] -= dt
            elif self.directionsb[i] == 'left' and abs(self.posbY[i] - self.posLGiro[0]) < dif:
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[1]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[0]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[1]) < dif:
                    self.directionsb[i] = 'down'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[0]) < dif:
                    self.directionsb[i] = 'down'
                else:
                    self.posbX[i] -= dt

            elif self.directionsb[i] == 'right' and abs(self.posbY[i] - self.posRGiro[1]) < dif:
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[1]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[0]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[1]) < dif:
                    self.directionsb[i] = 'down'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[0]) < dif:
                    self.directionsb[i] = 'down'
                if self.directionsb[i - 1] == 'left':
                    if self.posbY[i] < self.posbY[i - 1]:
                        if abs(self.posbX[i] - self.posUGiro[1]) < dif:
                            self.directionsb[i] = 'up'
                        else:
                            self.posbX[i] += dt
                    if self.posbX[i] > self.posbX[i - 1]:
                        if abs(self.posbY[i] - self.posDGiro[1]) < dif:
                            self.directionsb[i] = 'down'
                        else:
                            self.posbX[i] += dt
                else:
                    self.posbX[i] += dt
            elif self.directionsb[i] == 'right' and abs(self.posbY[i] - self.posRGiro[0]) < dif:
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[1]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'up' and abs(self.posbX[i] - self.posUGiro[0]) < dif:
                    self.directionsb[i] = 'up'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[1]) < dif:
                    self.directionsb[i] = 'down'
                if self.directionsb[i - 1] == 'down' and abs(self.posbX[i] - self.posDGiro[0]) < dif:
                    self.directionsb[i] = 'down'
                else:
                    self.posbX[i] += dt


    def move_up(self):
        if self.direction == 'down':
            return
        else:
            self.direction = 'up'
            self.posUGiro[1],self.posUGiro[0] = self.posX,self.posUGiro[1]
            self.rotate = 2 * math.pi

    def move_down(self):
        if self.direction == 'up':
            return
        else:
            self.direction = 'down'
            self.posDGiro[1],self.posDGiro[0] = self.posX,self.posDGiro[1]
            self.rotate = math.pi

    def move_right(self):
        if self.direction == 'left':
            return
        else:
            self.direction = 'right'
            self.posRGiro[1],self.posRGiro[0] = self.posY,self.posRGiro[1]
            self.rotate = -math.pi / 2

    def move_left(self):
        if self.direction == 'right':
            return
        else:
            self.direction = 'left'
            self.posLGiro[1],self.posLGiro[0] = self.posY,self.posLGiro[1]
            self.rotate = math.pi / 2


def readFaceVertex(faceDescription):
    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]

    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex


def readOBJ(filename, color):
    vertices = []
    normals = []
    textCoords = []
    faces = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split(' ')

            if aux[0] == 'v':
                vertices += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                textCoords += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'f':
                N = len(aux)
                faces += [[readFaceVertex(faceVertex) for faceVertex in aux[1:4]]]
                for i in range(3, N - 1):
                    faces += [[readFaceVertex(faceVertex) for faceVertex in [aux[i], aux[i + 1], aux[1]]]]

        vertexData = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0, 3):
                vertex = vertices[face[i][0] - 1]
                normal = normals[face[i][2] - 1]

                vertexData += [
                    vertex[0], vertex[1], vertex[2],
                    color[0], color[1], color[2],
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3

        return bs.Shape(vertexData, indices)
class Apple(object):
    def __init__(self):
        # figura base
        gpuApple = es.toGPUShape(shape=readOBJ('carrot.obj', (1, 0.5, 0.5)))
        apple = sg.SceneGraphNode('apple')
        apple.transform = tr.matmul([tr.rotationX(math.pi/2),tr.uniformScale(1 / 10)])
        apple.childs += [gpuApple]
        apple_tr = sg.SceneGraphNode('appleTR')
        apple_tr.childs += [apple]
        self.model = apple_tr
        self.x = 1
        self.y = 8
        self.collideOn = False
        self.apple = apple
        self.carrot = gpuApple
        self.count = 0
    def draw(self, pipeline):
        x = self.x * 1 / 20
        y = self.y * 1 / 20
        self.model.transform = tr.translate(x, y,-1/16)
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

    def cambiarP(self):
        x = random.choice(range(-20+2, 20-1, 1))
        y = random.choice(range(-20+2, 20 - 1, 1))
        self.x = x
        self.y = y

    def collide(self, xs, ys):
        x = self.x * 1/20
        y = self.y * 1/20
        if abs(x - xs) < 1/20 and abs(y - ys) < 1/20:
            self.collideOn = True
            self.count += 1
            self.cambiarP()


class Camara(object):
    def __init__(self):
        self.camX = 0
        self.camY = -0.5
    def camara1(self,dt,direction,posX,posY):
        if direction == 'up':
            if self.camX < 0:
                self.camX = min(self.camX, 0)
                self.camX += dt
            else:
                self.camX = max(self.camX, 0)
                self.camX -= dt
            self.camY = max(self.camY, -0.4)
            self.camY -= dt
        elif direction == 'left':
            self.camX = min(self.camX, 0.4)
            self.camX += dt
            if self.camY < 0:
                self.amY = min(self.camY, 0)
                self.camY += dt
            else:
                self.camY = max(self.camY, 0)
                self.camY -= dt
        elif direction == 'down':
            if self.camX < 0:
                self.camX = min(self.camX, 0)
                self.camX += dt
            else:
                self.camX = max(self.camX, 0)
                self.camX -= dt
            self.camY = min(self.camY, 0.4)
            self.camY += dt
        elif direction =='right':
            self.camX = max(self.camX, -0.4)
            self.camX -= dt
            if self.camY < 0:
                self.camY = min(self.camY, 0)
                self.camY += dt
            else:
                self.camY = max(self.camY, 0)
                self.camY -= dt

        view = tr.lookAt(
            np.array([posX+self.camX, posY+self.camY, 0.4]),  # eye
            np.array([posX, posY, 0.2]),  # At
            np.array([0, 0, 1]))  # up
        return view,posX+self.camX, posY+self.camY, 0.5

    def Camara2(self):
        view = tr.lookAt(
            np.array([0, 0, 1.85]),  # eye
            np.array([0.000001, 0.0000001, 0]),  # At
            np.array([0, 1, 1]))  # up
        return view
    def Camara3(self):
        view = tr.lookAt(
            np.array([-1, -1, 1.9]),  # eye
            np.array([-0.3, -0.3, 0]),  # At
            np.array([0, 0, 1]))  # up
        return view
class cielito(object):
    def __init__(self):
        gpuSky = es.toGPUShape(bs.createTextureQuad("img/cielo.png"), GL_REPEAT, GL_NEAREST)
        sky = sg.SceneGraphNode('cielo')
        sky.transform =tr.matmul([tr.rotationX(math.pi/2),tr.rotationY(math.pi/2),
                                   tr.translate(1,0.5,1),tr.uniformScale(2.1)])
        sky.childs += [gpuSky]
        skyRight = sg.SceneGraphNode('cieloDerecha')
        skyRight.transform = tr.translate(1/20,-1,0.5)
        skyRight.childs += [sky]
        skyLeft = sg.SceneGraphNode('cieloIzquierda')
        skyLeft.transform = tr.translate(-2-1/20, -1, 0.5)

        skyLeft.childs += [sky]
        skyFront = sg.SceneGraphNode('cieloFrente')
        skyFront.transform = tr.matmul([tr.rotationZ(-math.pi/2),tr.translate(-2-1/20, -1, 0.5)])
        skyFront.childs += [sky]
        skyBack = sg.SceneGraphNode('cieloFrente')
        skyBack.transform = tr.matmul([tr.rotationZ(math.pi / 2), tr.translate(-2 - 1 / 20, -1, 0.5)])
        skyBack.childs += [sky]
        cielo = sg.SceneGraphNode('cieloFinal')
        cielo.childs += [skyRight,skyLeft,skyFront,skyBack]

        self.sky = cielo
    def draw(self,pipeline):
        sg.drawSceneGraphNode(self.sky, pipeline, 'model')

class gameOver(object):
    def __init__(self):
        gpuGG = es.toGPUShape(bs.createTextureQuad("img/gg2.png"), GL_REPEAT, GL_NEAREST)
        GG = sg.SceneGraphNode('gg')
        GG.transform = tr.translate(0,0,1)
        GG.childs += [gpuGG]
        GG_tr = sg.SceneGraphNode('ggTR')
        GG_tr.childs += [gpuGG]
        self.model = GG
        self.o = 0.001
        self.t = GG_tr
        self.rotate =math.pi
    def draw(self, pipeline):
        self.model.transform = tr.matmul([tr.uniformScale(self.o),tr.rotationZ(self.rotate)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

    def xd(self,dt):
            self.rotate-= dt*1.556
            self.o += dt











