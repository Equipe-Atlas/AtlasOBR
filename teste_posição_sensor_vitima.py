from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor 
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])

hub.light.on(Color.RED)

motorgar = Motor(Port.E)
motorsel = Motor(Port.C)

cor = ColorSensor(Port.F)
cores = (Color.GREEN, Color.RED, Color.BLACK, Color.WHITE, Color.NONE, Color.BLUE)
cor.detectable_colors(cores)

omnitrix = StopWatch()

while True:
    color = cor.color()
    print(color)