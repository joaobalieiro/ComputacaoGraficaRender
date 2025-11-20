from typing import Tuple, Optional
from OpenGL.GL import *
from OpenGL import GLUT

# Quatro botoes para objetos
OBJECT_BUTTONS = [
    ("cube", "Cubo"),
    ("pyramid", "Piramide"),
    ("cylinder", "Cilindro"),
    ("sphere", "Esfera"),
]

# Tres botoes para modelo de iluminacao
SHADING_BUTTONS = [
    ("flat", "Flat"),
    ("gouraud", "Gouraud"),
    ("phong", "Phong"),
]

def _object_button_rects(width: int, height: int):
    margin = 10
    btn_w = 110
    btn_h = 30
    gap = 10
    # primeira linha (topo) para objetos
    y = height - margin - btn_h
    rects = []
    for i, (oid, _) in enumerate(OBJECT_BUTTONS):
        x = margin + i * (btn_w + gap)
        rects.append((oid, x, y, x + btn_w, y + btn_h))
    return rects


def _shading_button_rects(width: int, height: int):
    margin = 10
    btn_w = 110
    btn_h = 30
    gap = 10
    # segunda linha para modelos de iluminacao
    y = height - 2 * margin - 2 * btn_h
    rects = []
    for i, (sid, _) in enumerate(SHADING_BUTTONS):
        x = margin + i * (btn_w + gap)
        rects.append((sid, x, y, x + btn_w, y + btn_h))
    return rects


def draw_ui(width: int, height: int, current_object: str, current_shading: str) -> None:
    # UI sempre desenhada com pipeline fixo
    glUseProgram(0)

    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # fundo da barra superior
    glColor4f(0.0, 0.0, 0.0, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(0.0, height)
    glVertex2f(width, height)
    glVertex2f(width, height - 90.0)
    glVertex2f(0.0, height - 90.0)
    glEnd()

    # botoes de objeto
    for (oid, label), (_, x0, y0, x1, y1) in zip(OBJECT_BUTTONS, _object_button_rects(width, height)):
        if oid == current_object:
            glColor3f(0.2, 0.6, 0.9)
        else:
            glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(x0, y0)
        glVertex2f(x1, y0)
        glVertex2f(x1, y1)
        glVertex2f(x0, y1)
        glEnd()

        glColor3f(1.0, 1.0, 1.0)
        _draw_text(x0 + 8, y0 + 8, label)

    # botoes de modelo de iluminacao
    for (sid, label), (_, x0, y0, x1, y1) in zip(SHADING_BUTTONS, _shading_button_rects(width, height)):
        if sid == current_shading:
            glColor3f(0.8, 0.5, 0.2)
        else:
            glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(x0, y0)
        glVertex2f(x1, y0)
        glVertex2f(x1, y1)
        glVertex2f(x0, y1)
        glEnd()

        glColor3f(1.0, 1.0, 1.0)
        _draw_text(x0 + 8, y0 + 8, label)

    # restaura matrizes
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glPopAttrib()

def _draw_text(x: float, y: float, text: str) -> None:
    glRasterPos2f(x, y)
    for ch in text:
        GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord(ch))

def hit_test(x: int, y: int, width: int, height: int) -> Tuple[Optional[str], Optional[str]]:
    # Retorna ("object", id) ou ("shading", id) se clicou em algum botao
    # GLUT fornece y com origem no topo; nossa UI usa origem em baixo
    y_gl = height - y

    # testa botoes de objeto
    for oid, x0, y0, x1, y1 in _object_button_rects(width, height):
        if x0 <= x <= x1 and y0 <= y_gl <= y1:
            return "object", oid

    # testa botoes de shading
    for sid, x0, y0, x1, y1 in _shading_button_rects(width, height):
        if x0 <= x <= x1 and y0 <= y_gl <= y1:
            return "shading", sid

    return None, None
