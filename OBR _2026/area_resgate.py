from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Color, Direction
from pybricks.tools import wait
from pybricks.robotics import DriveBase

hub = PrimeHub()

motor_garra = Motor(Port.A)
motor_palheta = Motor(Port.B)
motor_esq = Motor(Port.C, positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.D)
sensor_cor = ColorSensor(Port.E)

robo = DriveBase(motor_esq, motor_dir, wheel_diameter=63, axle_track=133)

Color.SILVER = Color(h=180, s=10, v=80) 
sensor_cor.detectable_colors([Color.BLACK, Color.SILVER, Color.WHITE])

def resgate():
    print("Iniciando resgate...")
    motor_garra.run_target(speed=300, target_angle=0)
    wait(200)
    robo.straight(30)
    motor_garra.run_target(speed=400, target_angle=150)
    wait(500)
    cor_vitima = sensor_cor.color()
    print("Cor detectada:", cor_vitima)
    
    if cor_vitima == Color.SILVER:
        print("Vítima Prata")
        motor_palheta.run_target(speed=200, target_angle=60)
    elif cor_vitima == Color.BLACK:
        print("Vítima preta")
        motor_palheta.run_target(speed=200, target_angle=-60)
    else:
        print("Nada detectado.")
        motor_garra.run_target(speed=300, target_angle=0)
        robo.straight(-30)
        return

    motor_garra.run_target(speed=300, target_angle=220)
    wait(500)    
    motor_palheta.run_target(speed=200, target_angle=0)
    motor_garra.run_target(speed=300, target_angle=0)

def varredura_cega():
    for i in range(8):
        robo.straight(150)
        resgate()
        robo.turn(45)       

print("varredura comeca")
varredura_cega()
robo.stop()
print("acabo")