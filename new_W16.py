import sys
import math
import os
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

WIDTH, HEIGHT = 1280, 720

# Váriaveis Globais
cam_yaw = 35.0 
cam_pitch = 20.0  
cam_dist = 20.0   
car_yaw = 0.0    
drs_open = False
drs_angle = 0.0   
wheel_spin = 0.0  
drive_offset = 0.0  
drive_vel = 0.0     
drive_max = 18.0    
drive_accel = 12.0  
drive_brake = 18.0  
drive_active = False 

# Criando/Localizando as texturas com pygame
quadric = None
nose_tex_id = None
tyre_tex_id = None
logo_tex_id = None
engine_tex_id = None
hud_font = None
NOSE_TEXTURE_PATH = os.path.join(os.path.dirname(__file__), "nose_texture.png")
TYRE_TEXTURE_PATH = os.path.join(os.path.dirname(__file__), "pneu_texture.jpg")
LOGO_TEXTURE_PATH = os.path.join(os.path.dirname(__file__), "logo_side.png")
ENGINE_TEXTURE_PATH = os.path.join(os.path.dirname(__file__), "engine_cover_atlas.png")

# Cores pré criadas
def set_metal_black():
    glColor3f(0.03, 0.03, 0.04)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.4, 0.4, 0.4, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 40.0)

def set_metal_turquoise():
    glColor3f(0.0, 0.8, 0.8)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.6, 0.9, 0.9, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 80.0)

def set_dark_gray():
    glColor3f(0.22, 0.22, 0.26)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.25, 0.25, 0.25, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 22.0)

def set_carbon():
    glColor3f(0.05, 0.05, 0.06)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20.0)

def load_texture(path):
    if not os.path.exists(path):
        return None
    try:
        surf = pygame.image.load(path).convert_alpha()
        data = pygame.image.tostring(surf, "RGBA", True)
        w, h = surf.get_size()
    except Exception:
        return None
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id

def draw_cube(size):
    """Cubo sólido sem GLUT."""
    hs = size * 0.5
    glBegin(GL_QUADS)
    # +X
    glNormal3f(1, 0, 0)
    glVertex3f(hs, -hs, -hs); glVertex3f(hs, hs, -hs); glVertex3f(hs, hs, hs); glVertex3f(hs, -hs, hs)
    # -X
    glNormal3f(-1, 0, 0)
    glVertex3f(-hs, -hs, hs); glVertex3f(-hs, hs, hs); glVertex3f(-hs, hs, -hs); glVertex3f(-hs, -hs, -hs)
    # +Y
    glNormal3f(0, 1, 0)
    glVertex3f(-hs, hs, -hs); glVertex3f(hs, hs, -hs); glVertex3f(hs, hs, hs); glVertex3f(-hs, hs, hs)
    # -Y
    glNormal3f(0, -1, 0)
    glVertex3f(-hs, -hs, hs); glVertex3f(hs, -hs, hs); glVertex3f(hs, -hs, -hs); glVertex3f(-hs, -hs, -hs)
    # +Z
    glNormal3f(0, 0, 1)
    glVertex3f(-hs, -hs, hs); glVertex3f(-hs, hs, hs); glVertex3f(hs, hs, hs); glVertex3f(hs, -hs, hs)
    # -Z
    glNormal3f(0, 0, -1)
    glVertex3f(hs, -hs, -hs); glVertex3f(hs, hs, -hs); glVertex3f(-hs, hs, -hs); glVertex3f(-hs, -hs, -hs)
    glEnd()

def draw_sphere(radius, slices=20, stacks=20):
    gluSphere(quadric, radius, slices, stacks)

def draw_torus(inner, outer, sides=24, rings=48):
    r = inner
    R = outer
    for i in range(rings):
        theta = 2 * math.pi * i / rings
        theta_n = 2 * math.pi * (i + 1) / rings
        glBegin(GL_QUAD_STRIP)
        for j in range(sides + 1):
            phi = 2 * math.pi * j / sides
            cos_p, sin_p = math.cos(phi), math.sin(phi)
            for th in (theta, theta_n):
                cos_t, sin_t = math.cos(th), math.sin(th)
                x = (R + r * cos_p) * cos_t
                y = r * sin_p
                z = (R + r * cos_p) * sin_t
                nx = cos_p * cos_t
                ny = sin_p
                nz = cos_p * sin_t
                glNormal3f(nx, ny, nz)
                glVertex3f(x, y, z)
        glEnd()

def draw_text(x, y, text, color=(0.85, 0.95, 1.0)):
    """Desenha texto 2D na HUD sem GLUT, usando pygame para rasterizar."""
    global hud_font
    if hud_font is None:
        pygame.font.init()
        hud_font = pygame.font.Font(None, 18)
    surf = hud_font.render(text, True, tuple(int(c * 255) for c in color[:3]))
    data = pygame.image.tostring(surf, "RGBA", True)
    w, h = surf.get_size()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glPixelZoom(1, -1)  # vira para alinhar com ortho (y crescente para baixo)
    glRasterPos2f(x, y)  # posição do topo
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glPixelZoom(1, 1)

def init_gl():
    global quadric

    glClearColor(0.55, 0.75, 0.95, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    light0_pos = [15.0, 20.0, 10.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    light1_pos = [-20.0, 8.0, -15.0, 1.0]
    glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.2, 0.2, 0.4, 1.0])

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_NORMALIZE)

    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricTexture(quadric, GL_TRUE)

    reshape(WIDTH, HEIGHT)

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = float(w) / float(h)
    gluPerspective(55.0, aspect, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)


def setup_camera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad_y = math.radians(cam_yaw)
    rad_x = math.radians(cam_pitch)

    eye_x = cam_dist * math.cos(rad_x) * math.sin(rad_y) + drive_offset
    eye_y = cam_dist * math.sin(rad_x)
    eye_z = cam_dist * math.cos(rad_x) * math.cos(rad_y)
    center_x = drive_offset

    gluLookAt(
        eye_x, eye_y, eye_z,
        center_x, 0.8, 0.0,
        0.0, 1.0, 0.0
    )

def draw_ground():
    glDisable(GL_LIGHTING)
    size = 80.0

    glBegin(GL_QUADS)
    glColor3f(0.82, 0.82, 0.85)
    glVertex3f(-size, 0.0, -size)
    glVertex3f( size, 0.0, -size)
    glVertex3f( size, 0.0,  size)
    glVertex3f(-size, 0.0,  size)
    glEnd()

    glLineWidth(2.5)
    glColor3f(0.6, 0.6, 0.6)
    glBegin(GL_LINES)
    glVertex3f(-size, 0.001, 0.0)
    glVertex3f( size, 0.001, 0.0)
    glEnd()

    glEnable(GL_LIGHTING)

def draw_scenery():
    glDisable(GL_LIGHTING)
    
    glColor3f(0.16, 0.24, 0.14)
    size = 200.0
    glBegin(GL_QUADS)
    glVertex3f(-size, -0.02, -size)
    glVertex3f( size, -0.02, -size)
    glVertex3f( size, -0.02,  size)
    glVertex3f(-size, -0.02,  size)
    glEnd()
    
    glBegin(GL_TRIANGLES)
    glColor3f(0.20, 0.26, 0.18)
    for hx, hz in [(-60,-40),(60,-30),(-50,50),(70,60),(-70,0),(55,10)]:
        glVertex3f(hx, 0.0, hz)
        glVertex3f(hx+30, 0.0, hz+10)
        glVertex3f(hx+12, 25.0, hz+5)
    glEnd()
    
    glColor4f(1.0, 1.0, 1.0, 0.7)
    glBegin(GL_QUADS)
    clouds = [
        (-40, 60, 14, 8),
        (10, 80, 16, 7),
        (55, 65, 18, 9),
        (-70, -50, 20, 10),
        (35, -70, 15, 8),
    ]
    for cx, cz, sx, sz in clouds:
        y = 32.0
        glVertex3f(cx - sx, y, cz - sz)
        glVertex3f(cx + sx, y, cz - sz)
        glVertex3f(cx + sx, y, cz + sz)
        glVertex3f(cx - sx, y, cz + sz)
    glEnd()
    glEnable(GL_LIGHTING)


def pista_infinita(cx=0.0, cz=0.0):
    glDisable(GL_LIGHTING)
    track_half = 8
    stripe_gap = 0.10
    stripe_w = 0.45
    span = 500.0  

    x0 = cx - span * 0.5
    x1 = cx + span * 0.5

    # asfalto
    glColor3f(0.10, 0.10, 0.12)
    glBegin(GL_QUADS)
    glVertex3f(x0, 0.0, -track_half)
    glVertex3f(x1, 0.0, -track_half)
    glVertex3f(x1, 0.0,  track_half)
    glVertex3f(x0, 0.0,  track_half)
    glEnd()

    # zebras
    stripes = int(span // 3)
    seg = span / stripes
    for i in range(stripes):
        sx0 = x0 + i * seg
        sx1 = sx0 + seg
        is_red = (i & 1) == 0
        color = (0.85, 0.05, 0.05) if is_red else (0.95, 0.95, 0.95)
        glColor3f(*color)
        glBegin(GL_QUADS)
        # direita
        glVertex3f(sx0, 0.002, track_half + stripe_gap)
        glVertex3f(sx1, 0.002, track_half + stripe_gap)
        glVertex3f(sx1, 0.002, track_half + stripe_gap + stripe_w)
        glVertex3f(sx0, 0.002, track_half + stripe_gap + stripe_w)
        # esquerda
        glVertex3f(sx0, 0.002, -track_half - stripe_gap - stripe_w)
        glVertex3f(sx1, 0.002, -track_half - stripe_gap - stripe_w)
        glVertex3f(sx1, 0.002, -track_half - stripe_gap)
        glVertex3f(sx0, 0.002, -track_half - stripe_gap)
        glEnd()

    glColor3f(0.14, 0.22, 0.14)
    margin = track_half + stripe_gap + stripe_w
    glBegin(GL_QUADS)
    glVertex3f(x0, 0.0,  margin)
    glVertex3f(x1, 0.0,  margin)
    glVertex3f(x1, 0.0,  margin + 8.0)
    glVertex3f(x0, 0.0,  margin + 8.0)
    glVertex3f(x0, 0.0, -margin - 8.0)
    glVertex3f(x1, 0.0, -margin - 8.0)
    glVertex3f(x1, 0.0, -margin)
    glVertex3f(x0, 0.0, -margin)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_wheel():
    global quadric, tyre_tex_id
    glPushMatrix()
    set_metal_black()
    glRotatef(180, 0, 1, 0)
    glRotatef(wheel_spin, 0, 0, 1)

    tyre_radius = 0.70
    tyre_width = 0.80
    rim_radius = 0.22
    rim_width = 0.20

    glPushMatrix()
    use_tex = tyre_tex_id is not None
    if use_tex:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tyre_tex_id)
    glTranslatef(0, 0, -tyre_width * 0.5)
    gluCylinder(quadric, tyre_radius, tyre_radius, tyre_width, 64, 1)
    if use_tex:
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
    glNormal3f(0, 0, -1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(33):
        a = 2 * math.pi * i / 32
        glVertex3f(math.cos(a) * tyre_radius, math.sin(a) * tyre_radius, 0)
    glEnd()
    glNormal3f(0, 0, 1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, tyre_width)
    for i in range(33):
        a = 2 * math.pi * i / 32
        glVertex3f(math.cos(a) * tyre_radius, math.sin(a) * tyre_radius, tyre_width)
    glEnd()
    glPopMatrix()

    # aro
    glPushMatrix()
    glTranslatef(0, 0, -rim_width * 0.5)
    gluCylinder(quadric, rim_radius, rim_radius, rim_width, 24, 1)
    # tampas do aro
    glNormal3f(0, 0, -1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(25):
        a = 2 * math.pi * i / 24
        glVertex3f(math.cos(a) * rim_radius, math.sin(a) * rim_radius, 0)
    glEnd()
    glNormal3f(0, 0, 1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, rim_width)
    for i in range(25):
        a = 2 * math.pi * i / 24
        glVertex3f(math.cos(a) * rim_radius, math.sin(a) * rim_radius, rim_width)
    glEnd()
    glPopMatrix()

    # porca central
    glPushMatrix()
    set_metal_black()
    draw_sphere(0.06, 20, 20)
    glPopMatrix()
    glPopMatrix()


def draw_front_wheels():
    x = 3.5  # roda um pouco mais à frente
    y = -0.10
    zoff = 1.30

    glPushMatrix()
    glTranslatef(x, y, zoff)
    draw_wheel()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x, y, -zoff)
    draw_wheel()
    glPopMatrix()

def draw_rear_wheels():
    x = -2.6
    y = -0.01
    zoff = 1.5

    glPushMatrix()
    glTranslatef(x, y, zoff)
    glScalef(1.1, 1.1, 1.1)
    draw_wheel()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x, y, -zoff)
    glScalef(1.1, 1.1, 1.1)
    draw_wheel()
    glPopMatrix()

def draw_front_suspension():
    set_dark_gray()
    attach_x = 4
    attach_y_top = -0.05
    attach_y_bot = -0.22
    attach_z = 0.0
    wheel_x = 3.2
    wheel_y = -0.20
    zoff = 1.30           
    glLineWidth(6.0)
    glBegin(GL_LINES)
    for side in [1, -1]:
        s = float(side)
        # braço superior
        glVertex3f(attach_x, attach_y_top, attach_z + 0.28 * s)
        glVertex3f(wheel_x, wheel_y + 0.05, zoff * s)
        # braço inferior
        glVertex3f(attach_x - 0.15, attach_y_bot, attach_z + 0.30 * s)
        glVertex3f(wheel_x - 0.08, wheel_y - 0.05, zoff * s)
    glEnd()
    glLineWidth(1.0)

def draw_main_body():
    glPushMatrix()
    set_metal_black()
    glTranslatef(-0.52, 0.0, 0.0)  
    glScalef(4.6, 0.6, 1.25)     
    draw_cube(1.0)
    glPopMatrix()
    set_carbon()
    for side in [1, -1]:
        s = float(side)
        glBegin(GL_QUADS)
        glVertex3f(2.20, 0.08, 0.70 * s)
        glVertex3f(2.60, 0.04, 0.36 * s)
        glVertex3f(2.60, -0.12, 0.36 * s)
        glVertex3f(2.20, -0.08, 0.70 * s)
        glEnd()
    draw_side_logo()

def draw_side_logo():
    global logo_tex_id
    if logo_tex_id is None:
        return
    logo_w = 1.6
    logo_h = 0.42
    z_offset = 0.70
    x_center = 0.60
    y_center = 0.12
    glColor3f(1.0, 1.0, 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, logo_tex_id)
    for side in [1, -1]:
        s = float(side)
        u0, u1 = (0.0, 1.0) if s > 0 else (1.0, 0.0)
        glPushMatrix()
        glTranslatef(x_center, y_center, s * z_offset)
        glBegin(GL_QUADS)
        glNormal3f(0, 0, s)
        glTexCoord2f(u0, 0.0); glVertex3f(-logo_w * 0.5, -logo_h * 0.5, 0)
        glTexCoord2f(u1, 0.0); glVertex3f( logo_w * 0.5, -logo_h * 0.5, 0)
        glTexCoord2f(u1, 1.0); glVertex3f( logo_w * 0.5,  logo_h * 0.5, 0)
        glTexCoord2f(u0, 1.0); glVertex3f(-logo_w * 0.5,  logo_h * 0.5, 0)
        glEnd()
        glPopMatrix()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)


def draw_cockpit_and_halo():
    global quadric

    glPushMatrix()
    set_carbon()
    glTranslatef(-0.0, 0.70, 0.0)
    glRotatef(180, 1, 0, 0)
    glScalef(1.25, 1.0, 0.88)
    draw_torus(0.06, 0.52, 32, 52)
    glPopMatrix()
    glPushMatrix()
    set_carbon()
    glTranslatef(0.63, 0.70, 0.0)
    glRotatef(90, 1, 0, 0)
    glRotatef(20, 0, 4, 0)
    gluCylinder(quadric, 0.058, 0.044, 0.62, 18, 1)
    glPopMatrix()

def draw_floor_ground_effect():
    y = -0.22 
    set_carbon()
    glBegin(GL_QUADS)
    glVertex3f(1.8, y, 0.35)
    glVertex3f(1.8, y, -0.35)
    glVertex3f(-3.2, y, -0.35)
    glVertex3f(-3.2, y, 0.35)
    glEnd()

    set_carbon()
    for side in [1, -1]:
        s = float(side)

        glBegin(GL_QUADS)
        glVertex3f(1.8,  y, 0.35 * s)   
        glVertex3f(-3.0, y, 0.40 * s)   

        glVertex3f(-2.8, y, 1.15 * s)   
        glVertex3f(1.5,  y, 0.80 * s)   
        glEnd()

        glBegin(GL_QUADS)
        glVertex3f(1.5,  y, 0.80 * s)
        glVertex3f(-2.8, y, 1.15 * s)
        glVertex3f(-3.3, y, 1.35 * s)
        glVertex3f(0.0,  y, 1.25 * s)
        glEnd()

    set_metal_black()
    altura_borda = 0.20
    for side in [1, -1]:
        s = float(side)

        glBegin(GL_QUADS)
        # frente borda
        glVertex3f(0.0, y, 1.25 * s)
        glVertex3f(0.0, y + altura_borda, 1.25 * s)
        glVertex3f(-3.3, y + altura_borda, 1.35 * s)
        glVertex3f(-3.3, y, 1.35 * s)
        glEnd()
    for side in [1, -1]:
        s = float(side)
        glBegin(GL_QUADS)
        set_metal_turquoise()
        glVertex3f(0.8, y, 0.80 * s)
        glVertex3f(0.2, y, 0.95 * s)
        glVertex3f(0.0, 0.10, 1.00 * s)
        glVertex3f(0.5, 0.10, 0.90 * s)
        glEnd()


def draw_engine_cover_and_fin():
    global engine_tex_id
    glPushMatrix()
    glTranslatef(-1.6, 0.30, 0.0)
    front_top  = ( 1.9, 1, 0.0)
    front_left = ( 1.9, 0.00, 0.55)
    front_right= ( 1.9, 0.00,-0.55)
    rear_top   = (-1.5,0.28, 0.0)
    rear_left  = (-1.2,0.00, 0.65)
    rear_right = (-1.2,0.00,-0.65)

    use_tex = engine_tex_id is not None
    if use_tex:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, engine_tex_id)
        glColor3f(1.0, 1.0, 1.0)
        x_min, x_max = -1.5, 1.9
        z_min, z_max = -0.65, 0.65
        def uv(x, z):
            u = (x - x_min) / (x_max - x_min)
            v = (z - z_min) / (z_max - z_min)
            return u, v
    else:
        set_metal_black()

    glBegin(GL_TRIANGLES)
    # frente
    glNormal3f(0,0.6,1)
    if use_tex:
        glTexCoord2f(*uv(*front_left[::2])); glVertex3f(*front_left)
        glTexCoord2f(*uv(*front_right[::2])); glVertex3f(*front_right)
        glTexCoord2f(*uv(*front_top[::2])); glVertex3f(*front_top)
    else:
        glVertex3f(*front_left); glVertex3f(*front_right); glVertex3f(*front_top)
    # traseira
    glNormal3f(0,0.7,-1)
    if use_tex:
        glTexCoord2f(*uv(*rear_left[::2])); glVertex3f(*rear_left)
        glTexCoord2f(*uv(*rear_top[::2])); glVertex3f(*rear_top)
        glTexCoord2f(*uv(*rear_right[::2])); glVertex3f(*rear_right)
    else:
        glVertex3f(*rear_left); glVertex3f(*rear_top); glVertex3f(*rear_right)
    glEnd()

    # laterais
    glBegin(GL_QUADS)
    glNormal3f(0,-1,0)
    if use_tex:
        glTexCoord2f(*uv(*front_left[::2])); glVertex3f(*front_left)
        glTexCoord2f(*uv(*front_right[::2])); glVertex3f(*front_right)
        glTexCoord2f(*uv(*rear_right[::2])); glVertex3f(*rear_right)
        glTexCoord2f(*uv(*rear_left[::2])); glVertex3f(*rear_left)
    else:
        glVertex3f(*front_left); glVertex3f(*front_right); glVertex3f(*rear_right); glVertex3f(*rear_left)
    glNormal3f(0.2,0.1,1)
    if use_tex:
        glTexCoord2f(*uv(*front_left[::2])); glVertex3f(*front_left)
        glTexCoord2f(*uv(*front_top[::2])); glVertex3f(*front_top)
        glTexCoord2f(*uv(*rear_top[::2])); glVertex3f(*rear_top)
        glTexCoord2f(*uv(*rear_left[::2])); glVertex3f(*rear_left)
    else:
        glVertex3f(*front_left); glVertex3f(*front_top); glVertex3f(*rear_top); glVertex3f(*rear_left)
    glNormal3f(0.2,0.1,-1)
    if use_tex:
        glTexCoord2f(*uv(*front_right[::2])); glVertex3f(*front_right)
        glTexCoord2f(*uv(*rear_right[::2])); glVertex3f(*rear_right)
        glTexCoord2f(*uv(*rear_top[::2])); glVertex3f(*rear_top)
        glTexCoord2f(*uv(*front_top[::2])); glVertex3f(*front_top)
    else:
        glVertex3f(*front_right); glVertex3f(*rear_right); glVertex3f(*rear_top); glVertex3f(*front_top)
    glEnd()
    if use_tex:
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    glPushMatrix()
    set_dark_gray()
    glTranslatef(0.12, 1.2, 0.0)
    glScalef(0.20, 0.14, 0.24)
    draw_cube(2.0)
    glPopMatrix()

    glPushMatrix()
    set_carbon()
    glTranslatef(-2.7, 1.0, 0.0)
    glScalef(1.8, 0.7, 0.05)
    draw_cube(1.0)
    glPopMatrix()

def draw_endplate_shape():
    thickness = 0.06
    prof = [
        (0.00, 0.00),   # base esquerda
        (0.00, 0.75),   # topo esquerdo mais baixo
        (0.18, 0.75),   # início do arco
        (0.55, 0.60),   # meio do arco suavizado
        (0.70, 0.32),   # fim do arco descendente
        (0.70, 0.00)    # base direita curta
    ]
    glNormal3f(1,0,0)
    glBegin(GL_POLYGON)
    for z,y in prof:
        glVertex3f(thickness/2, y, z)
    glEnd()
    glNormal3f(-1,0,0)
    glBegin(GL_POLYGON)
    for z,y in reversed(prof):
        glVertex3f(-thickness/2, y, z)
    glEnd()
    glBegin(GL_QUADS)
    for i in range(len(prof)-1):
        z0,y0 = prof[i]; z1,y1 = prof[i+1]
        glNormal3f(0,0,1)
        glVertex3f(-thickness/2, y0, z0); glVertex3f(thickness/2, y0, z0)
        glVertex3f(thickness/2, y1, z1); glVertex3f(-thickness/2, y1, z1)
    glEnd()
    z0,y0 = prof[0]; z1,y1 = prof[-1]
    glNormal3f(0,1,0)
    glBegin(GL_QUADS)
    glVertex3f(-thickness/2, prof[1][1], prof[1][0]); glVertex3f(thickness/2, prof[1][1], prof[1][0])
    glVertex3f(thickness/2, prof[2][1], prof[2][0]); glVertex3f(-thickness/2, prof[2][1], prof[2][0])
    glEnd()
    glNormal3f(0,-1,0)
    glBegin(GL_QUADS)
    glVertex3f(-thickness/2, 0.0, z0); glVertex3f(thickness/2, 0.0, z0)
    glVertex3f(thickness/2, 0.0, z1); glVertex3f(-thickness/2, 0.0, z1)
    glEnd()

def draw_endplate_left():
    glPushMatrix()
    set_metal_black()
    glTranslatef(4.15, -0.35, -2.20)
    glRotatef(90, 0, 1, 0)
    draw_endplate_shape()
    glPopMatrix()

def draw_endplate_right():
    glPushMatrix()
    set_metal_black()
    glTranslatef(4.15, -0.35, 2.20)
    glRotatef(90, 0, 1, 0)
    draw_endplate_shape()
    glPopMatrix()

def draw_front_wing_detailed():
    global quadric
    set_dark_gray()
    def nose_slice(t):
        x = 2.6 + (5.30 - 2.6) * t
        w_base = 0.40 + (0.20 - 0.40) * t
        w = w_base + 0.010 * math.sin(math.pi * t)
        arc = -0.22 * (t ** 1.2)
        top_base = 0.30 + (0.06 - 0.30) * t
        bottom_base = 0.00 + (-0.18 + 0.00) * t
        top_y = top_base + arc
        bottom_y = bottom_base + arc * 0.75
        return x, top_y, bottom_y, w
    slices = [nose_slice(t) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]

    # topo
    use_tex = nose_tex_id is not None
    if use_tex:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, nose_tex_id)
    else:
        glDisable(GL_TEXTURE_2D)

    glNormal3f(0, 1, 0)
    glBegin(GL_QUAD_STRIP)

    n_slices = len(slices) - 1
    for i, (x, top_y, _, w) in enumerate(slices):
        v = i / float(n_slices)
        glTexCoord2f(0.0, v)
        glVertex3f(x, top_y, -w)

        # lado direito (z positivo)
        glTexCoord2f(1.0, v)
        glVertex3f(x, top_y,  w)

    glEnd()

    # fundo
    glBegin(GL_QUAD_STRIP); glNormal3f(0, -1, 0)
    for i,(x, _, bot_y, w) in enumerate(slices):
        v = i / float(n_slices)
        glTexCoord2f(0.0, v); glVertex3f(x, bot_y,  w)
        glTexCoord2f(1.0, v); glVertex3f(x, bot_y, -w)
    glEnd()
    # lado esquerdo
    glBegin(GL_QUAD_STRIP); glNormal3f(0, 0, 1)
    for i,(x, top_y, bot_y, w) in enumerate(slices):
        v = i / float(n_slices)
        glTexCoord2f(0.0, 0.0); glVertex3f(x, bot_y, w)
        glTexCoord2f(0.0, 1.0); glVertex3f(x, top_y, w)
    glEnd()
    # lado direito
    glBegin(GL_QUAD_STRIP); glNormal3f(0, 0, -1)
    for i,(x, top_y, bot_y, w) in enumerate(slices):
        v = i / float(n_slices)
        glTexCoord2f(1.0, 0.0); glVertex3f(x, bot_y, -w)
        glTexCoord2f(1.0, 1.0); glVertex3f(x, top_y, -w)
    glEnd()
    # tampa traseira
    x, top_y, bot_y, w = slices[0]
    glBegin(GL_QUADS); glNormal3f(-1, 0, 0)
    glTexCoord2f(0.0,0.0); glVertex3f(x, bot_y, -w)
    glTexCoord2f(1.0,0.0); glVertex3f(x, bot_y,  w)
    glTexCoord2f(1.0,1.0); glVertex3f(x, top_y,  w)
    glTexCoord2f(0.0,1.0); glVertex3f(x, top_y, -w)
    glEnd()
    x, top_y, bot_y, w = slices[-1]
    tip_x = x + 0.22
    tip_w = w * 0.22
    tip_top = top_y - 0.03
    tip_bot = bot_y - 0.02
    if use_tex:
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
    set_metal_black()

    glBegin(GL_QUADS)
    # topo
    glNormal3f(0,1,0)
    glTexCoord2f(0.0,0.0); glVertex3f(x,   top_y,  w)
    glTexCoord2f(1.0,0.0); glVertex3f(tip_x, tip_top,  tip_w)
    glTexCoord2f(1.0,1.0); glVertex3f(tip_x, tip_top, -tip_w)
    glTexCoord2f(0.0,1.0); glVertex3f(x,   top_y, -w)
    # base
    glNormal3f(0,-1,0)
    glTexCoord2f(0.0,0.0); glVertex3f(x,   bot_y,  w)
    glTexCoord2f(1.0,0.0); glVertex3f(x,   bot_y, -w)
    glTexCoord2f(1.0,1.0); glVertex3f(tip_x, tip_bot, -tip_w)
    glTexCoord2f(0.0,1.0); glVertex3f(tip_x, tip_bot,  tip_w)
    # lateral esquerda
    glNormal3f(0,0,1)
    glTexCoord2f(0.0,0.0); glVertex3f(x, bot_y, w)
    glTexCoord2f(1.0,0.0); glVertex3f(tip_x, tip_bot, tip_w)
    glTexCoord2f(1.0,1.0); glVertex3f(tip_x, tip_top, tip_w)
    glTexCoord2f(0.0,1.0); glVertex3f(x, top_y, w)
    # lateral direita
    glNormal3f(0,0,-1)
    glTexCoord2f(0.0,0.0); glVertex3f(x, bot_y, -w)
    glTexCoord2f(1.0,0.0); glVertex3f(x, top_y, -w)
    glTexCoord2f(1.0,1.0); glVertex3f(tip_x, tip_top, -tip_w)
    glTexCoord2f(0.0,1.0); glVertex3f(tip_x, tip_bot, -tip_w)
    glEnd()
    glNormal3f(1,0,0)
    glColor3f(0.02, 0.02, 0.02)
    glBegin(GL_QUADS)
    glVertex3f(tip_x, tip_bot, -tip_w); glVertex3f(tip_x, tip_top, -tip_w)
    glVertex3f(tip_x, tip_top,  tip_w); glVertex3f(tip_x, tip_bot,  tip_w)
    glEnd()

    z_neutral = 0.42
    z_outer   = 2.15
    segments  = 20

    for side in [1, -1]:
        s = float(side)

        # MAINPLANE (placa de baixo)
        set_carbon()
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            t = i / float(segments)  # 0..1

            z = s * (z_neutral + (z_outer - z_neutral) * t)

            front_x = 5.35 - 0.76 * t    # aproxima ainda mais do nariz
            back_x  = 4.85 - 0.46 * t
            y_main  = -0.30 + 0.012 * t  # alinhado ao rake da 4a flap

            glVertex3f(front_x, y_main,       z)
            glVertex3f(back_x,  y_main + 0.01, z)
        glEnd()

        # FLAP 1 (placa intermediária)
        set_dark_gray()
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            t = i / float(segments)

            z = s * (z_neutral + (z_outer - z_neutral) * t)

            front_x = 5.18 - 0.74 * t
            back_x  = 4.78 - 0.46 * t
            y_flap1 = -0.26 + 0.012 * t

            glVertex3f(front_x, y_flap1,       z)
            glVertex3f(back_x,  y_flap1 + 0.01, z)
        glEnd()

        # FLAP 2 (placa superior)
        set_dark_gray()
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            t = i / float(segments)

            z = s * (z_neutral + (z_outer - z_neutral) * t)

            front_x = 5.05 - 0.72 * t    
            back_x  = 4.62 - 0.44 * t
            y_flap2 = -0.22 + 0.012 * t

            glVertex3f(front_x, y_flap2,       z)
            glVertex3f(back_x,  y_flap2 + 0.01, z)
        glEnd()

    # FLAP 4 – contínua de endplate a endplate com formato em "triângulo"
    set_metal_black()
    span = z_outer + 0.08
    seg_f4 = 30
    front_base, back_base = 5.82, 5.25 
    front_taper, back_taper = 1.00, 0.70
    y_front_base, y_back_base = -0.30, -0.34
    y_gain = 0.012
    glBegin(GL_QUAD_STRIP)
    for i in range(seg_f4 + 1):
        z = -span + (2 * span * i / seg_f4)
        zn = abs(z) / span
        front = front_base - front_taper * zn
        back = back_base - back_taper * zn
        y_f = y_front_base + y_gain * zn
        y_b = y_back_base + y_gain * zn * 0.9
        glVertex3f(front, y_f, z)
        glVertex3f(back,  y_b, z)
    glEnd()
    draw_endplate_left()
    draw_endplate_right()



def draw_rear_wing_detailed():
    global drs_angle

    for side in [1, -1]:
        glPushMatrix()
        set_carbon()
        glTranslatef(-2.80, 0.50, side * 0.90)
        glRotatef(90,0,1,0)
        glScalef(0.12, 1.80, 0.70)
        draw_cube(1.0)
        glPopMatrix()

    for side in [0.2, -0.2]:
        glPushMatrix()
        set_carbon()
        glTranslatef(-3.20, 0.72, side)
        glScalef(0.10, 1, 0.14)
        draw_cube(1.0)
        glPopMatrix()

    glPushMatrix()
    set_carbon()
    glTranslatef(-2.90, 1.2, 0.0)
    glScalef(0.80, 0 , 1.68)
    draw_cube(1.0)
    glPopMatrix()

    glPushMatrix()
    set_metal_turquoise()
    glTranslatef(-3.10, 1.30, 0.0)  # eixo frontal do flap
    glRotatef(drs_angle, 0, 0, 1)   # abertura
    glTranslatef(0.06, 0.04, 0.0)   # desloca corpo após rotação
    glScalef(0.50, 0.0, 1.68)
    draw_cube(1.0)
    glPopMatrix()

def draw_exhaust():
    global quadric
    glPushMatrix()
    set_carbon()
    glTranslatef(-3.9, 0.78, 0.0)
    glRotatef(10, 0, 0, 1)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, 0.08, 0.06, 0.45, 16, 1)
    glPopMatrix()


def main_carro():
    glPushMatrix()
    glTranslatef(0.0, 0.80, 0.0)
    draw_main_body()
    glPushMatrix()
    glTranslatef(0.40, 0.0, 0.0)
    draw_cockpit_and_halo()
    glPopMatrix()
    draw_floor_ground_effect()
    draw_engine_cover_and_fin()
    glPushMatrix()
    glTranslatef(-0.8, 0.0, 0.0)
    draw_front_wing_detailed()
    draw_front_wheels()
    draw_front_suspension()
    glPopMatrix()
    draw_rear_wing_detailed()
    draw_rear_wheels()
    draw_exhaust()
    glPopMatrix()


def update_logic(dt):
    global car_yaw, drs_angle, drs_open, drive_offset, wheel_spin, drive_vel

    target = drive_max if drive_active else 0.0
    if drive_vel < target:
        drive_vel = min(drive_vel + drive_accel * dt, target)
    elif drive_vel > target:
        drive_vel = max(drive_vel - drive_brake * dt, target)

    drive_offset += drive_vel * dt
    spin_speed = (drive_vel / 0.70) * (180.0 / math.pi)  # deg/s baseado no raio do pneu
    wheel_spin = (wheel_spin + spin_speed * dt) % 360.0
    target = 20.0 if drs_open else 0.0  
    speed = 90.0 
    if abs(drs_angle - target) > 0.1:
        if drs_angle < target:
            drs_angle += speed * dt
        else:
            drs_angle -= speed * dt
    drs_angle = max(0.0, min(20.0, drs_angle))


def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_camera()
    draw_scenery()
    pista_infinita(drive_offset, 0.0)

    glPushMatrix()
    glTranslatef(drive_offset, 0.0, 0.0)  
    glRotatef(car_yaw, 0.0, 1.0, 0.0)
    main_carro()
    glPopMatrix()

    draw_hud()
    pygame.display.flip()


def handle_input():
    global cam_yaw, cam_pitch, cam_dist, drs_open, drive_active

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == VIDEORESIZE:
            reshape(event.w, event.h)

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_w:
                cam_dist = max(10.0, cam_dist - 1.0)
            elif event.key == K_s:
                cam_dist = min(40.0, cam_dist + 1.0)
            elif event.key == K_d:
                drs_open = not drs_open
            elif event.key == K_SPACE:
                drive_active = True   
            elif event.key in (K_LCTRL, K_RCTRL):
                drive_active = False  

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        cam_yaw -= 1.5
    if keys[K_RIGHT]:
        cam_yaw += 1.5
    if keys[K_UP]:
        cam_pitch = min(cam_pitch + 1.0, 80.0)
    if keys[K_DOWN]:
        cam_pitch = max(cam_pitch - 1.0, -5.0)


def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(10, 10)
    glVertex2f(330, 10)
    glVertex2f(330, 120)
    glVertex2f(10, 120)
    glEnd()

    glColor3f(0.85, 0.95, 1.0)
    lines = [
        "Controles:",
        "Espaço: acelerar/retomar",
        "Ctrl: frear",
        "D: abre/fecha DRS",
        "Setas / W,S: mover camera",
        "Esquerda/Direita: girar camera",
        "Esc: sair"
    ]
    y = 30
    glDisable(GL_TEXTURE_2D)
    for line in lines:
        draw_text(20, y, line)
        y += 18

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("Mercedes F1 - W16")

    init_gl()
    global nose_tex_id, tyre_tex_id, logo_tex_id, engine_tex_id
    nose_tex_id = load_texture(NOSE_TEXTURE_PATH)
    tyre_tex_id = load_texture(TYRE_TEXTURE_PATH)
    logo_tex_id = load_texture(LOGO_TEXTURE_PATH)
    engine_tex_id = load_texture(ENGINE_TEXTURE_PATH)

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000.0  # delta time em segundos
        handle_input()
        update_logic(dt)
        draw_scene()


if __name__ == "__main__":
    main()
