from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.MAGENTA)

cores = ColorSensor(Port.F)

Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240, s=100, v=50)
Color.WHITE = Color(h=0, s=0, v=100)
Color.GREEN = Color(h=186, s=80, v=50)
Color.RED = Color(h=0, s=100, v=50)
cores_ler = (Color.SILVER, Color.BLACK, Color.WHITE, Color.GREEN, Color.RED)
cores.detectable_colors(cores_ler)

while True:
    cor = cores.color()
    hsv = cores.hsv()
    print("cor:", cor, "| h:", hsv.h, "s:", hsv.s, "v:", hsv.v)
    wait(20)