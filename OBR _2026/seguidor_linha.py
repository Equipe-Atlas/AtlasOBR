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

andar = DriveBase(motor_esq, motor_dir, 63, 133)
andar.settings(straight_speed=100, straight_acceleration=300, turn_rate=100, turn_acceleration=300)

Color.SILVER = Color(h=0, s=0, v=75)
cores = (Color.GREEN, Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE)
cordir.detectable_colors(cores)
coresq.detectable_colors(cores)

reflection = 36  
vel = 150        
kp = 5
ki = 0.01
kd = 25
integral = 0
erro_anterior = 0
ultimo_dist = 0

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (100 <= dados.h <= 160) and (dados.s > 45) and (20 <= dados.v <= 70):
        return True
    return False

hub.light.on(Color.BLUE)

while True:
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    dist = ultra.distance()
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    if dist < 120:
        ultimo_dist = dist
        motor_esq.run(-50)
        motor_dir.run(50)
        wait(500)
        dist = ultra.distance()
        if dist > ultimo_dist:
            while dist > ultimo_dist:
                ultimo_dist = dist
                motor_esq.run(50)
                motor_dir.run(-50)
                wait(50)
                dist = ultra.distance()
        dist = ultra.distance()
        ultimo_dist = dist
        motor_esq.run(-50)
        motor_dir.run(50)
        wait(1000)
        dist = ultra.distance()
        while dist < ultimo_dist:
            ultimo_dist = dist
            motor_esq.run(-50)
            motor_dir.run(50)
            wait(50)
            dist = ultra.distance()
        andar.turn(130)
        andar.straight(200)
        andar.turn(-105)
        andar.straight(400)
        andar.turn(-105)
        andar.straight(200)
        andar.turn(-110)
        andar.straight(-30)
        motor_esq.run(-100)
        motor_dir.run(100)
        wait(1000)
        meio = cormeio.reflection()
        while meio > 80:
            motor_esq.run(-100)
            motor_dir.run(100)
            meio = cormeio.reflection()
        integral = 0
        erro_anterior = 0
    else:
        if esq_e_verde and dir_e_verde or esq == Color.GREEN and dir == Color.GREEN:
            andar.turn(-200)
            andar.straight(50)
        elif esq_e_verde or esq == Color.GREEN:
            while esq != Color.WHITE:
                motor_esq.run(-50)
                motor_dir.run(0)
                esq = coresq.color()
            andar.straight(15)
            dir = cordir.color()
            wait(100)
            if dir == Color.GREEN:
                andar.turn(-200)
                andar.straight(50)
            else:
                andar.straight(50)
                andar.turn(-90)
                andar.straight(50)
        elif dir_e_verde or dir == Color.GREEN:
            while dir != Color.WHITE:
                motor_esq.run(0)
                motor_dir.run(-50)
                dir = cordir.color()
            andar.straight(15)
            esq = coresq.color()
            wait(100)
            if esq == Color.GREEN:
                andar.turn(-200)
                andar.straight(50)
            else:
                andar.straight(50)
                andar.turn(90)
                andar.straight(50)
        else:
            if esq == Color.WHITE and meio > 90 and dir == Color.WHITE:
                motor_esq.run(vel)
                motor_dir.run(vel)
            elif dir == Color.BLACK and esq == Color.BLACK:
                motor_esq.run(vel)
                motor_dir.run(vel)
            else:
                erro = reflection - meio
                integral = integral + erro
                if integral > 100: integral = 100
                if integral < -100: integral = -100
                derivada = erro - erro_anterior
                correcao = (kp * erro) + (ki * integral) + (kd * derivada)
                if correcao > 200: correcao = 200
                elif correcao < -200: correcao = -200
                if dir != Color.WHITE and dir != Color.GREEN and meio > 15:
                    andar.straight(20)
                    meio = cormeio.reflection()
                    if meio > 60:
                        while meio > 60:
                            motor_esq.run(150)
                            motor_dir.run(-150)
                            meio = cormeio.reflection()
                elif esq != Color.WHITE and esq != Color.GREEN and meio > 15:
                    andar.straight(20)
                    meio = cormeio.reflection()
                    if meio > 60:
                        while meio > 60:
                            motor_esq.run(-150)
                            motor_dir.run(150)
                            meio = cormeio.reflection()
                motor_esq.run(vel + correcao)
                motor_dir.run(vel - correcao) 
                erro_anterior = erro
    wait(20)
    print("esquerda: {}, meio: {}, direita: {}, distância: {}".format(esq, meio, dir, dist))