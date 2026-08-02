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
    if (100 <= dados.h <= 160) and (dados.s > 45) and (20 <= dados.v <= 70):
        return True
    return False

bat = hub.battery.voltage()
print(bat)
while True:
    motor_esq.run(100)
    motor_dir.run(100)
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    dist = ultra.distance()
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    if dist < 100:
        andar.turn(80)
        ultimo_dist = ultra.distance()
        while dist <= ultimo_dist:
            ultimo_dist = ultra.distance()
            motor_esq.run(-100)
            motor_dir.run(100)
            wait(10)
            dist = ultra.distance()
            if dist > 300: dist = 300
            if ultimo_dist > 300: ultimo_dist = 300
            if dist > (ultimo_dist + 1): dist = ultimo_dist
            print("distância: {}, ultima: {}".format(dist, ultimo_dist))
        andar.turn(95)
        andar.stop()
        wait(999999)