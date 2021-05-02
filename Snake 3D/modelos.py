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
        self.o = 10
        self.direction = 'up'
        self.headS = head
        self.head = transform_head
        self.posX = 0
        self.posY = 0
        self.n = 0
        self.collideW = False
        self.rotate = 0
        self.stop = False
    def draw(self, pipeline):
        self.head.transform = tr.matmul([tr.translate(self.posX, self.posY, 0), tr.rotationZ(self.rotate)])
        sg.drawSceneGraphNode(self.head, pipeline, 'model')
    def collideWall(self):
        limit = 1-(1/20*1.55)
        if abs(self.posX - limit) < 0.001 or abs(self.posX + limit) < 0.001 or abs(self.posY - limit) < 0.001 or abs(
                self.posY + limit) < 0.001:
            self.collideW = True
            self.stop = True

    def update(self, dt):
        dif = 0.002
        if self.direction == 'right':
            self.posX += dt
        if self.direction == 'left':
            self.posX -= dt
        if self.direction == 'up':
            self.posY += dt
        if self.direction == 'down':
            self.posY -= dt

    def move_up(self):
        if self.direction == 'down':
            return
        else:
            self.direction = 'up'
            self.rotate = 2 * math.pi

    def move_down(self):
        if self.direction == 'up':
            return
        else:
            self.direction = 'down'
            self.rotate = math.pi

    def move_right(self):
        if self.direction == 'left':
            return
        else:
            self.direction = 'right'
            self.rotate = -math.pi / 2

    def move_left(self):
        if self.direction == 'right':
            return
        else:
            self.direction = 'left'
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











