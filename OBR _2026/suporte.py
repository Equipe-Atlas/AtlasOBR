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

andar = DriveBase(motor_esq, motor_dir, 63, 133)
andar.settings(straight_speed=100, straight_acceleration=300, turn_rate=100, turn_acceleration=300)

hub.imu.reset_heading(0)

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (150 <= dados.h <= 210) and (dados.s > 30) and (40 <= dados.v <= 110):
        return True
    return False

reflection = 36  
vel = 150       
kp = 4
ki = 0.01
kd = 20
integral = 0
erro_anterior = 0
ultimo_dist = 0
ultima_arfagem = 0
dirpreto = False
esqpreto = False

bat = hub.battery.voltage()
print(bat)
while True:
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    dist = ultra.distance()
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    arfagem, rolagem = hub.imu.tilt()
    arfagem = arfagem + 3.6
    hsv_esq = coresq.hsv()
    hsv_meio = cormeio.hsv()
    hsv_dir = cordir.hsv() 
    wait(20)
    guinada = hub.imu.heading()
    print("esquerda: {}, meio: {}, direita: {}, distância: {}, arfagem: {}".format(esq, meio, dir, dist, arfagem))
    if esq_e_verde:
        hub.light.on(Color.GREEN)
    else:
        hub.light.on(Color.RED)