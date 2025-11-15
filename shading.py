from OpenGL.GL import *

current_mode = "gouraud"
phong_program = None

def compile_shader(source: str, shader_type: int) -> int:
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if status != GL_TRUE:
        log = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Erro compilando shader: {log}")
    return shader

def link_program(vs: int, fs: int) -> int:
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    status = glGetProgramiv(prog, GL_LINK_STATUS)
    if status != GL_TRUE:
        log = glGetProgramInfoLog(prog).decode()
        raise RuntimeError(f"Erro linkando programa: {log}")
    return prog

def init_phong_shader() -> None:
    global phong_program

    # Agora o vertex shader também passa a cor do vértice (gl_Color)
    vertex_src = """
    varying vec3 vNormal;
    varying vec3 vFragPos;
    varying vec3 vColor;

    void main() {
        vec4 posView = gl_ModelViewMatrix * gl_Vertex;
        vFragPos = posView.xyz;
        vNormal = normalize(gl_NormalMatrix * gl_Normal);
        vColor = gl_Color.rgb;  // cor vinda do glColor3f no codigo em Python
        gl_Position = gl_ProjectionMatrix * posView;
    }
    """

    # Fragment shader usa vColor como cor base do material
    fragment_src = """
    varying vec3 vNormal;
    varying vec3 vFragPos;
    varying vec3 vColor;

    uniform vec3 uLightPos;        // em coordenadas de camera
    uniform vec3 uViewPos;         // normalmente (0,0,0) em view space
    uniform vec3 uSpecularColor;   // cor do especular (normalmente branca)
    uniform float uShininess;
    uniform float uAmbientStrength;
    uniform float uDiffuseStrength;

    void main() {
        vec3 N = normalize(vNormal);
        vec3 L = normalize(uLightPos - vFragPos);
        vec3 V = normalize(uViewPos - vFragPos);
        vec3 R = reflect(-L, N);

        float diff = max(dot(N, L), 0.0);
        float spec = 0.0;
        if (diff > 0.0) {
            spec = pow(max(dot(R, V), 0.0), uShininess);
        }

        // cor base do objeto vem de vColor (glColor)
        vec3 ambient  = uAmbientStrength  * vColor;
        vec3 diffuse  = diff * uDiffuseStrength * vColor;
        vec3 specular = spec * uSpecularColor;

        vec3 color = ambient + diffuse + specular;
        gl_FragColor = vec4(color, 1.0);
    }
    """

    vs = compile_shader(vertex_src, GL_VERTEX_SHADER)
    fs = compile_shader(fragment_src, GL_FRAGMENT_SHADER)
    phong_program = link_program(vs, fs)

def set_shading_mode(mode: str) -> None:
    global current_mode
    current_mode = mode

    if mode in ("flat", "gouraud"):
        glUseProgram(0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        if mode == "flat":
            glShadeModel(GL_FLAT)
        else:
            glShadeModel(GL_SMOOTH)
    elif mode == "phong":
        glDisable(GL_LIGHTING)     # desligamos a iluminacao fixa
        glUseProgram(phong_program)

def prepare_for_frame(shading_mode: str, light_pos, view_pos) -> None:
    if shading_mode == "phong":
        glUseProgram(phong_program)

        # parametros tipicos de Phong
        specular = (1.0, 1.0, 1.0)
        shininess = 32.0
        ambient_strength = 0.2
        diffuse_strength = 0.8

        loc_light = glGetUniformLocation(phong_program, b"uLightPos")
        loc_view = glGetUniformLocation(phong_program, b"uViewPos")
        loc_spec = glGetUniformLocation(phong_program, b"uSpecularColor")
        loc_shine = glGetUniformLocation(phong_program, b"uShininess")
        loc_ambs = glGetUniformLocation(phong_program, b"uAmbientStrength")
        loc_diffs = glGetUniformLocation(phong_program, b"uDiffuseStrength")

        glUniform3f(loc_light, float(light_pos[0]), float(light_pos[1]), float(light_pos[2]))
        glUniform3f(loc_view, float(view_pos[0]), float(view_pos[1]), float(view_pos[2]))
        glUniform3f(loc_spec, float(specular[0]), float(specular[1]), float(specular[2]))
        glUniform1f(loc_shine, float(shininess))
        glUniform1f(loc_ambs, float(ambient_strength))
        glUniform1f(loc_diffs, float(diffuse_strength))
    else:
        # flat/gouraud: volta para o pipeline fixo
        glUseProgram(0)

def finish_frame() -> None:
    if current_mode != "phong":
        glUseProgram(0)
