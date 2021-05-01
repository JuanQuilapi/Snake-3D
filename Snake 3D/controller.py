from mathlib import Point3
import camera as cam
import glfw
import sys
from typing import Union
from modelos import Snake

# A class to store the application control
class Controller(object):
    model: Union['Snake', None]


    def __init__(self):
        self.model = None
        self.nuca = True
        self.c2d = False
        self.perspectiva = False
    def set_model(self, m):
        self.model = m


    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return
        elif key == glfw.KEY_W and action == glfw.PRESS:
            self.model.move_up()
        elif key == glfw.KEY_S and action == glfw.PRESS:
            self.model.move_down()
        elif key == glfw.KEY_A and action == glfw.PRESS:
            if self.nuca:
                if self.model.direction == 'up':
                    self.model.move_left()
                elif self.model.direction == 'left':
                    self.model.move_down()
                elif self.model.direction == 'down':
                    self.model.move_right()
                else:  # direction == right
                    self.model.move_up()
            elif self.c2d or self.perspectiva:
                self.model.move_left()
        elif key == glfw.KEY_D and action == glfw.PRESS:
            if self.nuca:
                if self.model.direction == 'up':
                    self.model.move_right()
                elif self.model.direction == 'left':
                    self.model.move_up()
                elif self.model.direction == 'down':
                    self.model.move_left()
                else:  # direction == right
                    self.model.move_down()
            elif self.c2d or self.perspectiva:
                self.model.move_right()
        elif key == glfw.KEY_R and action == glfw.PRESS:
            self.nuca = True
            self.c2d = False
            self.perspectiva = False
        elif key == glfw.KEY_E and action == glfw.PRESS:
            self.c2d = True
            self.nuca = False
            self.perspectiva = False
        elif key == glfw.KEY_T and action == glfw.PRESS:
            self.c2d = False
            self.nuca = False
            self.perspectiva = True


        if key == glfw.KEY_ESCAPE:
            sys.exit()


