from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor 
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait
from pybricks.robotics import DriveBase

hub = PrimeHub(broadcast_channel=1, observe_channels=[2])

ultra = UltrasonicSensor(Port.C)
cordir = ColorSensor(Port.B)
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)

motor_esq = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E)

andar = DriveBase(motor_esq, motor_dir, 63, 133)
andar.settings(straight_speed=100, straight_acceleration=300, turn_rate=100, turn_acceleration=300)

hub.imu.reset_heading(0)

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (150 <= dados.h <= 180) and (dados.s > 30) and (50 <= dados.v <= 100):
        return True
    return False

bat = hub.battery.voltage()
print(bat)
while True:
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    dist = ultra.distance()
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    if esq_e_verde or dir_e_verde:
        hub.light.on(Color.GREEN)
    else:
        hub.light.on(Color.RED)
    print("H: {}, S: {}, V: {}".format(coresq.hsv().h, coresq.hsv().s, coresq.hsv().v))
    motor_esq.run(1200)
    motor_dir.run(1200)
    
