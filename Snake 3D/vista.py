import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import lighting_shaders as ls
import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
from controller import Controller
from modelos import *
import model
if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 900
    height = 800

    window = glfw.create_window(width, height, "Snake 3D", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)
    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    mvpPipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    pipeline = ls.SimpleGouraudShaderProgram()
    # Telling OpenGL to use our shader program
    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Hacemos los objetos
    Fondo = Fondo()
    Snake = Snake()
    Apple = Apple()
    Cam = Camara()
    Sky = cielito()
    GG = gameOver()
    controlador.set_model(Snake)

    # Using the same view and projection matrices in the whole application

    t0 = 0
    vt = 0
    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input
        # Calculamos el dt
        t1 = glfw.get_time()*5/20
        dt = t1 - t0
        t0 = t1
        # Using GLFW to check for input events
        glfw.poll_events()
        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(mvpPipeline.shaderProgram)
        projection = tr.perspective(60, float(width) / float(height), 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        if controlador.nuca:
            view1 = Cam.camara1(dt*3,Snake.direction,Snake.posX,Snake.posY)
            view = view1[0]
        elif controlador.c2d:
            view = Cam.Camara2()
        elif controlador.perspectiva:
            view = Cam.Camara3()
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        if not Snake.stop:
            Snake.update(dt)
        # logica
        Apple.collide(Snake.posX,Snake.posY)
        Snake.collideWall()
        if Snake.collideW:
            if GG.o < 2.014 and GG.rotate < 2 * math.pi:
                GG.xd(15 * dt)



        # DIBUJAR LOS MODELOS
        Fondo.draw(mvpPipeline)
        Snake.draw(mvpPipeline)
        Sky.draw(mvpPipeline)
        GG.draw(mvpPipeline)
        glUseProgram(pipeline.shaderProgram)


        lightPos = np.array([(Apple.x * 1 / 20 + 0.5)*np.cos(vt),(Apple.y * 1 / 20 + 0.5)*np.sin(vt), 0.4])
        vt += dt*33
        viewPos = Cam.camara1(dt*3,Snake.direction,Snake.posX,Snake.posY)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 0.3, 0.3, 0.3)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 0.3, 0.3, 0.3)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.3, 0.3, 0.3)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.3, 0.3, 0.3)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[1], viewPos[2],
                    viewPos[3])

        if Apple.count % 3 == 0:
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1], lightPos[2])
        else:
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 0,0,1.5)
            vt = 0
        if Apple.count % 3 == 0:

            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)
        else:
            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100000000)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        Apple.draw(pipeline)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)


    glfw.terminate()
