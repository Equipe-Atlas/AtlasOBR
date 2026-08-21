from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor 
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

hub = PrimeHub(broadcast_channel=1, observe_channels=[2])

ultra = UltrasonicSensor(Port.C)
cordir = ColorSensor(Port.B)
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)

motor_esq = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E)
Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240 < 170, s=40<1, v= 100 < 10)
cores = (Color.GREEN, Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE, Color.RED)
cordir.detectable_colors(cores)
coresq.detectable_colors(cores)

omnitrix = StopWatch()

while True:
    hub.light.on(Color.RED)
    if cordir.color() == Color.SILVER:
        hub.light.on(Color.GREEN)
    if coresq.color() == Color.SILVER:
        hub.light.on(Color.BLUE)
