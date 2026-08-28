from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

hub = PrimeHub()
ultra = UltrasonicSensor(Port.C)
cordir = ColorSensor(Port.B)
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)
motor_esq = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E)

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (160 <= dados.h <= 200) and (dados.s > 40) and (40 <= dados.v <= 100):
        return True
    return False

def e_preto(sensor):
    dados = sensor.hsv()
    if (dados.h > 160) and (dados.s < 60) and (dados.v < 80):
        return True
    return False

while True:
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    esq_preto = e_preto(coresq)
    dir_preto = e_preto(cordir)
    dist = ultra.distance()
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    arfagem, rolagem = hub.imu.tilt()
    arfagem = arfagem + 3.6
    hsv_esq = coresq.hsv()
    hsv_meio = cormeio.hsv()
    hsv_dir = cordir.hsv()
    print(hsv_esq.h, hsv_esq.s, hsv_dir.v)