from OpenGL.GL import *

# Modo de sombreamento atual usado pelo modulo shading
# Pode ser "flat", "gouraud" ou "phong"; inicia em "gouraud"
current_mode = "gouraud"

# Identificador do programa de shader Phong (GL handle)
# Sera definido em init_phong_shader() e usado quando current_mode == "phong"
phong_program = None

def compile_shader(source: str, shader_type: int) -> int:
    # Cria um objeto shader OpenGL do tipo indicado (vertex ou fragment)
    shader = glCreateShader(shader_type)

    # Associa o codigo fonte GLSL ao shader e solicita a compilacao
    glShaderSource(shader, source)
    glCompileShader(shader)

    # Verifica se a compilacao foi bem-sucedida
    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if status != GL_TRUE:
        log = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Erro compilando shader: {log}")

    # Retorna o identificador do shader compilado para uso em init_phong_shader()
    return shader

def link_program(vs: int, fs: int) -> int:
    # Cria um programa OpenGL vazio
    prog = glCreateProgram()

    # Anexa o vertex shader (vs) e o fragment shader (fs) ao programa
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)

    # Faz o link do programa combinando os dois shaders
    glLinkProgram(prog)

    # Verifica se o link foi bem-sucedido
    status = glGetProgramiv(prog, GL_LINK_STATUS)
    if status != GL_TRUE:
        log = glGetProgramInfoLog(prog).decode()
        raise RuntimeError(f"Erro linkando programa: {log}")

    # Retorna o handle do programa para uso em init_phong_shader()
    return prog

def init_phong_shader() -> None:
    global phong_program

    # Codigo fonte do vertex shader Phong:
    # calcula posicao em view space, normal e cor do vertice (vColor)
    # que serao usadas no fragment shader.
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

    # Codigo fonte do fragment shader Phong:
    # aplica iluminacao ambiente, difusa e especular,
    # usando vColor como cor base do material.
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

    # Compila vertex e fragment shader a partir das strings GLSL acima
    vs = compile_shader(vertex_src, GL_VERTEX_SHADER)
    fs = compile_shader(fragment_src, GL_FRAGMENT_SHADER)

    # Faz o link dos dois shaders em um programa unico.
    # O handle resultante e guardado em phong_program e usado
    # em set_shading_mode() e prepare_for_frame() quando o modo for "phong".
    phong_program = link_program(vs, fs)

def set_shading_mode(mode: str) -> None:
    # Atualiza o modo de sombreamento atual (flat, gouraud ou phong)
    global current_mode
    current_mode = mode

    if mode in ("flat", "gouraud"):
        # Volta para o pipeline fixo (sem shader programavel)
        glUseProgram(0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # Define modelo de sombreamento do OpenGL:
        # FLAT  -> cor constante por face
        # SMOOTH -> interpolacao por vertice (Gouraud)
        if mode == "flat":
            glShadeModel(GL_FLAT)
        else:
            glShadeModel(GL_SMOOTH)

    elif mode == "phong":
        # Desliga iluminacao fixa e ativa o programa Phong
        glDisable(GL_LIGHTING)
        glUseProgram(phong_program)

def prepare_for_frame(shading_mode: str, light_pos, view_pos) -> None:
    if shading_mode == "phong":
        # Ativa o programa de shader Phong para este frame
        glUseProgram(phong_program)

        # Parametros padrao do modelo de iluminacao Phong
        specular = (1.0, 1.0, 1.0)
        shininess = 32.0
        ambient_strength = 0.2
        diffuse_strength = 0.8

        # Localiza os uniforms no programa Phong
        loc_light = glGetUniformLocation(phong_program, b"uLightPos")
        loc_view = glGetUniformLocation(phong_program, b"uViewPos")
        loc_spec = glGetUniformLocation(phong_program, b"uSpecularColor")
        loc_shine = glGetUniformLocation(phong_program, b"uShininess")
        loc_ambs = glGetUniformLocation(phong_program, b"uAmbientStrength")
        loc_diffs = glGetUniformLocation(phong_program, b"uDiffuseStrength")

        # Envia posicao da luz, da camera e parametros de iluminacao ao shader
        glUniform3f(loc_light, float(light_pos[0]), float(light_pos[1]), float(light_pos[2]))
        glUniform3f(loc_view, float(view_pos[0]), float(view_pos[1]), float(view_pos[2]))
        glUniform3f(loc_spec, float(specular[0]), float(specular[1]), float(specular[2]))
        glUniform1f(loc_shine, float(shininess))
        glUniform1f(loc_ambs, float(ambient_strength))
        glUniform1f(loc_diffs, float(diffuse_strength))
    else:
        # Para flat/gouraud, garante uso do pipeline fixo (sem shader)
        glUseProgram(0)

def finish_frame() -> None:
    # Para modos que nao usam shader explicito, garante que nenhum programa
    # permaneça ativo apos o desenho (seguranca de estado)
    if current_mode != "phong":
        glUseProgram(0)
