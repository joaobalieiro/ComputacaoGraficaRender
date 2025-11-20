from typing import Literal
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import objects3d
import shading
import ui

# Dimensoes iniciais da janela (em pixels).
# Usadas em init_gl() e reshape() para configurar viewport e matriz de projecao,
# e em ui.draw_ui() para posicionar corretamente a barra de botoes na tela.
width = 800
height = 600

# Angulos iniciais de rotacao do objeto 3D em torno dos eixos X, Y e Z (em graus).
# Esses valores sao alterados pelas funcoes de teclado (keyboard() e special_keys())
# e aplicados em display(), antes de desenhar os objetos em objects3d.py.
angle_x = 20.0
angle_y = -30.0
angle_z = 0.0

# Parametros da camera (sistema de visualizacao):
# - eye: posicao da camera (de onde estamos olhando)
# - center: ponto para onde a camera esta apontando
# - up: vetor "para cima" que define a orientacao da camera
# Esses valores sao usados em apply_camera(), que chama gluLookAt(...)
# para montar a matriz de visualizacao antes de desenhar a cena.
eye_x = 0.0
eye_y = 0.0
eye_z = 8.0

center_x = 0.0
center_y = 0.0
center_z = 0.0

up_x = 0.0
up_y = 1.0
up_z = 0.0

# Modo de projecao usado para desenhar a cena:
# - "perspective": usa gluPerspective(), com efeito de profundidade (objetos distantes menores)
# - "orthographic": usa glOrtho(), sem perspectiva (tamanhos constantes)
# Esta variavel e lida em setup_projection() para configurar a matriz de projecao
# e pode ser alternada em keyboard() (tecla 'p'), afetando como os objetos de objects3d.py
# sao projetados e exibidos na janela.
projection: Literal["perspective", "orthographic"] = "perspective"

# objeto inicial selecionado pelos botoes
current_object = "cube"

# modelo inicial de iluminacao selecionado
current_shading = "gouraud"

light_pos = (4.0, 4.0, 4.0)

def init_gl(w: int, h: int) -> None:
    # Atualiza largura e altura globais da janela (usadas na projecao e na UI)
    global width, height
    width, height = w, h

    # Habilita teste de profundidade (controla quais objetos aparecem na frente)
    glEnable(GL_DEPTH_TEST)

    # Define cor de fundo usada em glClear() dentro de display()
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Habilita sistema de iluminacao fixa e a luz GL_LIGHT0
    # Usado nos modos de sombreamento flat e gouraud
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Permite que glColor defina componentes ambiente e difusa do material
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Configura componentes difusa e especular da luz GL_LIGHT0
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

    # Compila e linka o shader Phong definido em shading.py
    shading.init_phong_shader()

    # Configura a matriz de projecao inicial (perspective ou orthographic)
    setup_projection()

    # Ajusta o modo de sombreamento inicial (flat, gouraud ou phong)
    shading.set_shading_mode(current_shading)

def setup_projection() -> None:
    # Seleciona a matriz de projecao e zera seu conteudo
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Calcula proporcao largura/altura da janela para evitar distorcao
    aspect = width / float(height) if height > 0 else 1.0

    if projection == "perspective":
        # Projecao em perspectiva: objetos mais distantes parecem menores
        gluPerspective(45.0, aspect, 0.1, 100.0)
    else:
        # Projecao ortografica: sem efeito de perspectiva
        size = 6.0
        glOrtho(-size * aspect, size * aspect, -size, size, 0.1, 100.0)

    # Volta para a matriz de modelo/visualizacao usada em apply_camera() e display()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def apply_camera() -> None:
    # Reseta a matriz de modelo/visualizacao antes de posicionar a camera
    glLoadIdentity()

    # Define a matriz de visualizacao com gluLookAt
    gluLookAt(
        eye_x, eye_y, eye_z,
        center_x, center_y, center_z,
        up_x, up_y, up_z
    )

def display() -> None:
    # Limpa o framebuffer de cor e o buffer de profundidade
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Aplica a camera (matriz de visualizacao definida em apply_camera())
    apply_camera()

    # Define posicao da luz GL_LIGHT0 no espaco da camera
    # (usa light_pos global que pode ser lida em shading.py)
    glLightfv(GL_LIGHT0, GL_POSITION, (light_pos[0], light_pos[1], light_pos[2], 1.0))

    # Prepara o modo de sombreamento atual (flat, gouraud ou phong).
    # Em shading.prepare_for_frame() sao configurados:
    # - pipeline fixo (flat/gouraud) OU
    # - shader programavel (phong), com uniforms de luz e camera.
    shading.prepare_for_frame(
        shading_mode=current_shading,
        light_pos=light_pos,
        view_pos=(0.0, 0.0, 0.0),
    )

    # Transformacao global aplicada a todos os objetos desenhados em draw_scene_objects():
    # translacao para afastar no eixo Z e rotacoes controladas por teclado.
    glTranslatef(0.0, 0.0, -5.0)
    glRotatef(angle_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)
    glRotatef(angle_z, 0.0, 0.0, 1.0)

    # Desenha eixos e o objeto 3D escolhido (cubo, piramide, cilindro ou esfera)
    # definidos em objects3d.py
    draw_scene_objects()

    # Finaliza configuracoes de shading para este frame, se necessario
    shading.finish_frame()

    # Desenha a interface 2D (barra de botoes) em modo ortografico,
    # definida no modulo ui.py
    ui.draw_ui(width, height, current_object, current_shading)

    # Troca os buffers (double buffering) exibindo o frame pronto na tela
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
    # Atualiza dimensoes globais da janela (usadas na projecao e na UI)
    global width, height
    width, height = w, h

    # Ajusta a area de desenho OpenGL para cobrir toda a nova janela
    glViewport(0, 0, w, h)

    # Recalcula a matriz de projecao com o novo aspecto largura/altura
    setup_projection()

def timer(value: int) -> None:
    # Solicita redesenho da cena (chama display() no proximo ciclo do GLUT)
    glutPostRedisplay()

    # Agenda nova chamada do timer em ~16 ms (60 FPS)
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
    # da a opcao para o usuario usar as setas do teclado
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
    # Trata cliques do mouse sobre a barra de botoes da UI
    global current_object, current_shading

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Verifica se o clique caiu em algum botao definido em ui.py
        kind, value = ui.hit_test(x, y, width, height)

        if kind == "object":
            # Troca o objeto 3D exibido (cubo, piramide, cilindro, esfera)
            current_object = value
        elif kind == "shading":
            # Troca o modo de sombreamento e atualiza o estado em shading.py
            current_shading = value
            shading.set_shading_mode(current_shading)

        # Solicita redesenho para refletir a troca na tela
        glutPostRedisplay()
