from pybricks.hubs import PrimeHub
from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait

hub = PrimeHub()
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)
cordir = ColorSensor(Port.B)

while True:
    print("meio:", cormeio.reflection(), "esq:", coresq.color(), "dir:", cordir.color())
    wait(200)