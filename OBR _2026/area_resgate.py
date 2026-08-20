from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor 
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])

hub.light.on(Color.GREEN)

cores = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)

garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

omnitrix = StopWatch()

while True:
    dist_esq = ultra_esq.distance()
    dist_dir = ultra_dir.distance()
    if (dist_esq + dist_dir) < 110:
        hub.ble.broadcast(100)
        while hub.ble.broadcast() != 10000:
            if dist_esq < dist_dir:
                garra.run(10)