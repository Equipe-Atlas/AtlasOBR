from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

hub = PrimeHub(broadcast_channel=1, observe_channels=[2])
COD_ENTROU_AREA = 600
COD_ENTROU_CANTO = 100
COD_SAIDA_ESQ = 201
COD_SAIDA_FRENTE = 202
COD_SAIDA_DIR = 203
COD_PRECISA_GIRAR = 209
COD_LIBERA = 10000
COD_ANDA_FRENTE = 300
COD_GIRA_90 = 301
COD_PAUSA = 500

ultra = UltrasonicSensor(Port.C)
cordir = ColorSensor(Port.B)
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)
motor_esq = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E)
andar = DriveBase(motor_esq, motor_dir, 63, 133)
andar.settings(straight_speed=100, straight_acceleration=300, turn_rate=100, turn_acceleration=300)

Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240, s=100, v=20)
cores = (Color.GREEN, Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE, Color.RED)
cordir.detectable_colors(cores)
coresq.detectable_colors(cores)

omnitrix = StopWatch()
reflection = 36
vel = 150
kp = 5
ki = 0.01
kd = 20
integral = 0
erro_anterior = 0
ultimo_dist = 0
ultima_arfagem = 0
dirpreto = False
esqpreto = False
tempo = 0
na_area_resgate = False
passou_rampa = False
ultimo_comando = None

def na_area_resgate():
    andar.stop()
    dist = ultra.distance()
    hub.ble.broadcast(dist)
    mensagem = hub.ble.observe(2)
    if mensagem == COD_ENTROU_AREA:
        return True
    return False
    print(mensagem)

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (160 <= dados.h <= 210) and (dados.s > 40) and (40 <= dados.v <= 100):
        return True
    return False

hub.imu.reset_heading(0)
hub.light.on(Color.BLUE)

while True:
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    dist = ultra.distance()
    hub.ble.broadcast(dist)
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    arfagem, rolagem = hub.imu.tilt()
    arfagem = arfagem + 3.6
    hsv_esq = coresq.hsv()
    hsv_meio = cormeio.hsv()
    hsv_dir = cordir.hsv()
    mensagem = hub.ble.observe(2)
    vel = 150
    if arfagem > 5 or arfagem < -5:
        passou_rampa = True
        if arfagem > 3:
            vel = 300
        elif arfagem < -3:
            vel = 150
        hub.imu.reset_heading(0)
        while arfagem > 3 or arfagem < -3:
            guinada = hub.imu.heading()
            arfagem, rolagem = hub.imu.tilt()
            arfagem = arfagem + 3.6
            esq = coresq.color()
            dir = cordir.color()
            ad = 0
            ae = 0
            if dir == Color.BLACK:
                ae = 200
            elif esq == Color.BLACK:
                ad = 200
            motor_esq.run(guinada * -10 + vel + ae)
            motor_dir.run(guinada * 10 + vel + ad)
            wait(20)
    else:
        if na_area_resgate:
            hub.light.on(Color.RED)
            if mensagem == COD_PAUSA:
                andar.stop()
                while True:
                    msg = hub.ble.observe(2)
                    if msg == COD_LIBERA:
                        break
                    wait(20)
                ultimo_comando = None

            elif mensagem == COD_ENTROU_CANTO:
                andar.stop()
                ultima_msg = None
                achou_saida = False
                while True:
                    msg = hub.ble.observe(2)
                    if msg == COD_LIBERA:
                        if achou_saida:
                            na_area_resgate = False
                            hub.light.on(Color.BLUE)
                        break
                    elif msg != ultima_msg:
                        if msg == COD_SAIDA_ESQ:
                            andar.turn(-90)
                            achou_saida = True
                        elif msg == COD_SAIDA_FRENTE:
                            andar.straight(100)
                            achou_saida = True
                        elif msg == COD_SAIDA_DIR:
                            andar.turn(90)
                            achou_saida = True
                        elif msg == COD_PRECISA_GIRAR:
                            andar.turn(30)
                        ultima_msg = msg
                    wait(20)
            elif mensagem != ultimo_comando:
                if mensagem == COD_ANDA_FRENTE:
                    andar.straight(200)
                elif mensagem == COD_GIRA_90:
                    andar.turn(90)
                elif mensagem == COD_LIBERA:
                    andar.stop()
                ultimo_comando = mensagem

        # === SEGUE LINHA ===
        else:
            if dist < 90:
                andar.turn(80)
                ultimo_dist = ultra.distance()
                while dist <= ultimo_dist:
                    ultimo_dist = ultra.distance()
                    motor_esq.run(-100)
                    motor_dir.run(100)
                    wait(20)
                    dist = ultra.distance()
                    if dist > 300: dist = 300
                    if ultimo_dist > 300: ultimo_dist = 300
                    if dist > (ultimo_dist + 1): dist = ultimo_dist
                    print("distância: {}, ultima: {}".format(dist, ultimo_dist))
                andar.turn(100)
                andar.straight(200)
                andar.turn(-100)
                andar.straight(400)
                andar.turn(-100)
                andar.straight(200)
                andar.turn(-115)
                motor_esq.run(-100)
                motor_dir.run(100)
                wait(2500)
                meio = cormeio.reflection()
                while meio > 80:
                    motor_esq.run(-100)
                    motor_dir.run(100)
                    meio = cormeio.reflection()
                    wait(20)
                integral = 0
                erro_anterior = 0
            else:
                if esq_e_verde and dir_e_verde or esq == Color.GREEN and dir == Color.GREEN:
                    andar.turn(-200)
                    andar.straight(50)
                elif esq_e_verde or esq == Color.GREEN:
                    if dirpreto == False or esqpreto == False:
                        while esq != Color.WHITE:
                            motor_esq.run(-50)
                            motor_dir.run(-75)
                            esq = coresq.color()
                        andar.straight(20)
                        dir = cordir.color()
                        dir_e_verde = mapeia_verde(cordir)
                        wait(100)
                        if dir == Color.GREEN or dir_e_verde:
                            andar.turn(-200)
                            andar.straight(50)
                        else:
                            andar.straight(40)
                            andar.turn(-90)
                            andar.straight(40)
                    elif esqpreto == True or dirpreto == True:
                        andar.straight(50)
                        dirpreto = False
                        esqpreto = False
                elif dir_e_verde or dir == Color.GREEN:
                    if dirpreto == False or esqpreto == False:
                        while dir != Color.WHITE:
                            motor_esq.run(-75)
                            motor_dir.run(-50)
                            dir = cordir.color()
                        andar.straight(20)
                        dir = cordir.color()
                        esq_e_verde = mapeia_verde(coresq)
                        wait(100)
                        if esq == Color.GREEN or esq_e_verde:
                            andar.turn(-200)
                            andar.straight(50)
                        else:
                            andar.straight(40)
                            andar.turn(90)
                            andar.straight(40)
                        dirpreto = False
                    elif esqpreto == True or dirpreto == True:
                        andar.straight(50)
                        dirpreto = False
                        esqpreto = False
                else:
                    if esq != Color.BLACK and meio > 50 and dir != Color.BLACK:
                        motor_esq.run(vel)
                        motor_dir.run(vel)
                        wait(200)
                    elif dir == Color.BLACK and esq == Color.BLACK:
                        motor_esq.run(vel)
                        motor_dir.run(vel)
                        dirpreto = True
                        esqpreto = True
                        wait(500)
                    else:
                        erro = reflection - meio
                        integral = integral + erro
                        if integral > 100: integral = 100
                        if integral < -100: integral = -100
                        derivada = erro - erro_anterior
                        correcao = (kp * erro) + (ki * integral) + (kd * derivada)
                        if correcao > 300: correcao = 300
                        elif correcao < -300: correcao = -300
                        if dir == Color.BLACK:
                            dirpreto = True
                        elif esq == Color.BLACK:
                            esqpreto = True
                        motor_esq.run(vel + correcao)
                        motor_dir.run(vel - correcao)
                        erro_anterior = erro
                        dirpreto = False
                        esqpreto = False

    print("esquerda: {}, meio: {}, direita: {}, distância: {}, arfagem: {}".format(esq, meio, dir, dist, arfagem))
    wait(20)