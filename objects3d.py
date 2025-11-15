from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def draw_axes() -> None:
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)

    # X - vermelho
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    # Y - verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    # Z - azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()
    glEnable(GL_LIGHTING)


def draw_cube() -> None:
    glColor3f(0.8, 0.2, 0.2)

    # cubo centrado na origem, lado 2
    s = 1.0

    glBegin(GL_QUADS)

    # frente (z = +s)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-s, -s, s)
    glVertex3f(s, -s, s)
    glVertex3f(s, s, s)
    glVertex3f(-s, s, s)

    # trás (z = -s)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, -s, -s)

    # esquerda (x = -s)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, -s, s)
    glVertex3f(-s, s, s)
    glVertex3f(-s, s, -s)

    # direita (x = +s)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(s, -s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, s, s)
    glVertex3f(s, -s, s)

    # topo (y = +s)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-s, s, -s)
    glVertex3f(-s, s, s)
    glVertex3f(s, s, s)
    glVertex3f(s, s, -s)

    # base (y = -s)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-s, -s, -s)
    glVertex3f(s, -s, -s)
    glVertex3f(s, -s, s)
    glVertex3f(-s, -s, s)

    glEnd()


def draw_pyramid() -> None:
    glColor3f(0.2, 0.7, 0.2)

    # pirâmide de base quadrada, centrada na origem
    s = 1.0
    h = 1.5

    # vértices
    v0 = (-s, 0.0, -s)  # base
    v1 = (s, 0.0, -s)
    v2 = (s, 0.0, s)
    v3 = (-s, 0.0, s)
    top = (0.0, h, 0.0)

    glBegin(GL_TRIANGLES)

    # face 0-1-top
    glNormal3f(0.0, 0.6, -0.8)
    glVertex3f(*v0)
    glVertex3f(*v1)
    glVertex3f(*top)

    # face 1-2-top
    glNormal3f(0.8, 0.6, 0.0)
    glVertex3f(*v1)
    glVertex3f(*v2)
    glVertex3f(*top)

    # face 2-3-top
    glNormal3f(0.0, 0.6, 0.8)
    glVertex3f(*v2)
    glVertex3f(*v3)
    glVertex3f(*top)

    # face 3-0-top
    glNormal3f(-0.8, 0.6, 0.0)
    glVertex3f(*v3)
    glVertex3f(*v0)
    glVertex3f(*top)

    glEnd()

    # base
    glBegin(GL_QUADS)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(*v0)
    glVertex3f(*v1)
    glVertex3f(*v2)
    glVertex3f(*v3)
    glEnd()


def draw_cylinder() -> None:
    glColor3f(0.2, 0.4, 0.8)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)

    # cilindro ao longo de y
    glPushMatrix()
    glRotatef(-90.0, 1.0, 0.0, 0.0)  # alinhar eixo com Z
    gluCylinder(quad, 0.7, 0.7, 2.0, 32, 8)

    # tampa de baixo
    gluDisk(quad, 0.0, 0.7, 32, 1)
    # tampa de cima
    glTranslatef(0.0, 0.0, 2.0)
    gluDisk(quad, 0.0, 0.7, 32, 1)
    glPopMatrix()

    gluDeleteQuadric(quad)


def draw_sphere() -> None:
    glColor3f(0.7, 0.7, 0.1)
    glutSolidSphere(1.2, 40, 40)
