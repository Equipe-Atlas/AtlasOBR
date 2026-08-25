from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.MAGENTA)

ultra = UltrasonicSensor(Port.C)
cordir = ColorSensor(Port.B)
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)

Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240 < 170, s=40<1, v= 100 < 10)
cores = (Color.GREEN, Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE, Color.RED)
cordir.detectable_colors(cores)
coresq.detectable_colors(cores)

def mapeia_verde(sensor):                                                     #
    dados = sensor.hsv()                                                      #
    if (160 <= dados.h <= 200) and (dados.s < 40) and (40 <= dados.v <= 100): # função ler verde
        return True                                                           #
    return False                                                              #

omnitrix = StopWatch()

while True:
    esq_verde = mapeia_verde(coresq)
    esq = coresq.hsv()
    print(esq.h, esq.s, esq.v)
    esqcor = coresq.color()
    if esq_verde:
        hub.light.on(Color.GREEN)
    else:
        hub.light.on(Color.RED)
    wait(20)