from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor 
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])

hub.light.on(Color.GREEN)

motorgar = Motor(Port.E)
motorsel = Motor(Port.C)

cores = ColorSensor(Port.F)

omnitrix = StopWatch()

while True:
    cor = cores.color()
    if cor == Color.RED:
        hub.light.on(Color.RED)
    else:
        hub.light.on(Color.GREEN)