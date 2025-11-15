from OpenGL.GLUT import *
import scene

WIDTH = 800
HEIGHT = 600

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Trabalho 2 - TG3D e Modelos de Iluminacao")

    scene.init_gl(WIDTH, HEIGHT)

    glutDisplayFunc(scene.display)
    glutReshapeFunc(scene.reshape)
    glutKeyboardFunc(scene.keyboard)
    glutSpecialFunc(scene.special_keys)
    glutMouseFunc(scene.mouse)    # <-- mouse para clicar nos botoes
    glutTimerFunc(16, scene.timer, 0)

    glutMainLoop()

if __name__ == "__main__":
    main()
