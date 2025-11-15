from typing import Literal
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import objects3d
import shading
import ui

width = 800
height = 600

angle_x = 20.0
angle_y = -30.0
angle_z = 0.0

eye_x = 0.0
eye_y = 0.0
eye_z = 8.0

center_x = 0.0
center_y = 0.0
center_z = 0.0

up_x = 0.0
up_y = 1.0
up_z = 0.0

projection: Literal["perspective", "orthographic"] = "perspective"

# objeto selecionado pelos botoes
current_object = "cube"

# modelo de iluminacao selecionado
current_shading = "gouraud"

light_pos = (4.0, 4.0, 4.0)


def init_gl(w: int, h: int) -> None:
    global width, height
    width, height = w, h

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

    shading.init_phong_shader()

    setup_projection()
    shading.set_shading_mode(current_shading)


def setup_projection() -> None:
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    aspect = width / float(height) if height > 0 else 1.0

    if projection == "perspective":
        gluPerspective(45.0, aspect, 0.1, 100.0)
    else:
        size = 6.0
        glOrtho(-size * aspect, size * aspect, -size, size, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def apply_camera() -> None:
    glLoadIdentity()
    gluLookAt(
        eye_x, eye_y, eye_z,
        center_x, center_y, center_z,
        up_x, up_y, up_z
    )


def display() -> None:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    apply_camera()

    # luz no espaco da camera
    glLightfv(GL_LIGHT0, GL_POSITION, (light_pos[0], light_pos[1], light_pos[2], 1.0))

    # prepara shading (flat/gouraud/pong)
    shading.prepare_for_frame(
        shading_mode=current_shading,
        light_pos=light_pos,
        view_pos=(0.0, 0.0, 0.0),
    )

    # transformacao global do objeto
    glTranslatef(0.0, 0.0, -5.0)
    glRotatef(angle_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)
    glRotatef(angle_z, 0.0, 0.0, 1.0)

    draw_scene_objects()

    # encerra uso de shader (se necessario)
    shading.finish_frame()

    # desenha a UI 2D com os botoes
    ui.draw_ui(width, height, current_object, current_shading)

    glutSwapBuffers()


def draw_scene_objects() -> None:
    # eixos para referencia
    objects3d.draw_axes()

    # apenas um objeto por vez, escolhido pelos botoes
    if current_object == "cube":
        objects3d.draw_cube()
    elif current_object == "pyramid":
        objects3d.draw_pyramid()
    elif current_object == "cylinder":
        objects3d.draw_cylinder()
    elif current_object == "sphere":
        objects3d.draw_sphere()


def reshape(w: int, h: int) -> None:
    global width, height
    width, height = w, h
    glViewport(0, 0, w, h)
    setup_projection()


def timer(value: int) -> None:
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def keyboard(key: bytes, x: int, y: int) -> None:
    global projection, current_object, current_shading
    global eye_z, angle_x, angle_y, angle_z

    # ESC
    if key == b'\x1b':
        glutLeaveMainLoop()
        return

    # alternar projecao
    if key in (b'p', b'P'):
        projection = "perspective" if projection == "orthographic" else "orthographic"
        setup_projection()

    # aproximar/afastar camera
    if key == b'+':
        eye_z -= 0.5
    if key == b'-':
        eye_z += 0.5

    # --- W A S D para "mexer" a figura (rotacao) ---
    if key in (b'w', b'W'):
        angle_x += 5.0
    elif key in (b's', b'S'):
        angle_x -= 5.0
    elif key in (b'a', b'A'):
        angle_y -= 5.0
    elif key in (b'd', b'D'):
        angle_y += 5.0

    # opcional: Q/E para rotacao em Z
    if key in (b'q', b'Q'):
        angle_z += 5.0
    elif key in (b'e', b'E'):
        angle_z -= 5.0

    # atalhos opcionais de teclado para objetos
    if key == b'1':
        current_object = "cube"
    elif key == b'2':
        current_object = "pyramid"
    elif key == b'3':
        current_object = "cylinder"
    elif key == b'4':
        current_object = "sphere"

    # atalhos opcionais para shading
    if key in (b'f', b'F'):
        current_shading = "flat"
        shading.set_shading_mode(current_shading)
    if key in (b'g', b'G'):
        current_shading = "gouraud"
        shading.set_shading_mode(current_shading)
    if key in (b'h', b'H'):
        current_shading = "phong"
        shading.set_shading_mode(current_shading)

    glutPostRedisplay()


def special_keys(key: int, x: int, y: int) -> None:
    # se quiser manter as setas funcionando tambem
    global angle_x, angle_y, angle_z

    if key == GLUT_KEY_UP:
        angle_x += 5.0
    elif key == GLUT_KEY_DOWN:
        angle_x -= 5.0
    elif key == GLUT_KEY_LEFT:
        angle_y -= 5.0
    elif key == GLUT_KEY_RIGHT:
        angle_y += 5.0
    elif key == GLUT_KEY_PAGE_UP:
        angle_z += 5.0
    elif key == GLUT_KEY_PAGE_DOWN:
        angle_z -= 5.0

    glutPostRedisplay()


def mouse(button: int, state: int, x: int, y: int) -> None:
    """Trata clique do mouse nos botoes da UI."""
    global current_object, current_shading

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        kind, value = ui.hit_test(x, y, width, height)
        if kind == "object":
            current_object = value
        elif kind == "shading":
            current_shading = value
            shading.set_shading_mode(current_shading)
        glutPostRedisplay()
