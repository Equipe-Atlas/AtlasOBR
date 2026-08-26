from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

hub = PrimeHub(broadcast_channel=1, observe_channels=[2])

COD_ENTROU_CANTO = 100
COD_SAIDA_ESQ = 201
COD_SAIDA_FRENTE = 202
COD_SAIDA_DIR = 203
COD_LIBERA = 10000
COD_ANDA_FRENTE = 300
COD_GIRA_90 = 301
COD_GIRA_90N = 302
COD_PAUSA = 500
COD_PAREDE_ESQ = 502
COD_PAREDE_DIR = 503
COD_ALINHA = 401

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
Color.GREEN = Color(h=186, s=80, v=50)
cores = (Color.GREEN, Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE, Color.RED)
cordir.detectable_colors(cores)
coresq.detectable_colors(cores)

omnitrix = StopWatch()
busca = StopWatch()

reflection = 36
vel_base = 150
kp = 3.5
ki = 0
kd = 8
integral = 0
erro_anterior = 0
ultimo_erro = 0
ultimo_dist = 0
dirpreto = False
esqpreto = False
tempo = 0
passou_rampa = False
cooldown_obst = 0
vel_min = 70
estado = "linha"

dist_esq = 0
dist_dir = 0
dist_esq1 = 0
dist_dir1 = 0
pacote = 0, 0
gap = False

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (160 <= dados.h <= 210) and (dados.s > 40) and (40 <= dados.v <= 100):
        return True
    return False

<<<<<<< HEAD
def e_preto(sensor):
    dados = sensor.hsv()
    if (dados.h > 170) and (dados.s < 50) and (dados.v < 80):
        return True
    return False
=======
def ler_meio():
    total = 0
    for _ in range(3):
        total = total + cormeio.reflection()
        wait(5)
    return total // 3

def na_linha():
    return cormeio.reflection() < 25 or coresq.color() == Color.BLACK or cordir.color() == Color.BLACK
>>>>>>> 674e73e1a7324129a7c27e4c724eb1a521aebcf8

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
    mensagem = hub.ble.observe(2)
    if cooldown_obst > 0:
        cooldown_obst = cooldown_obst - 20
    if arfagem > 5 or arfagem < -5:
        passou_rampa = True
        vel_rampa = 300 if arfagem > 3 else 150
        hub.imu.reset_heading(0)
        while arfagem > 3 or arfagem < -3:
            guinada = hub.imu.heading()
            arfagem, rolagem = hub.imu.tilt()
            arfagem = arfagem + 3.6
            esq = coresq.color()
            dir = cordir.color()
            ae = 200 if dir == Color.BLACK else 0
            ad = 200 if esq == Color.BLACK else 0
            motor_esq.run(guinada * -10 + vel_rampa + ae)
            motor_dir.run(guinada * 10 + vel_rampa + ad)
            wait(20)
        estado = "linha"
        integral = 0
        erro_anterior = 0
    elif mensagem == 200:
        parede = 0
        vez = 1
        andar.straight(40)
        andar.stop()
        dist = ultra.distance()
        hub.ble.broadcast(dist)
        wait(1000)
        mensagem = hub.ble.observe(2)
        print(mensagem)
        if mensagem == 502: parede = 502
        elif mensagem == 503: parede = 503
        wait(500)
        while mensagem != 7777777:
            while vez != 3:
                if parede == 502:
                    wait(20)
                elif parede == 503:
                    dist = ultra.distance()
                    pacote = hub.ble.observe(2)
                    print(pacote)
                    dist_esq1, dist_dir1 = pacote
                    hub.imu.reset_heading(0)
                    while dist > 350:
                        pacote = hub.ble.observe(2)
                        dist_esq, dist_dir = pacote
                        dist = ultra.distance()
                        motor_esq.run(300 - (dist_dir1 - dist_dir) - (hub.imu.heading() * 2))
                        motor_dir.run(320 + (dist_dir1 - dist_dir) + (hub.imu.heading() * 2))
                        print(dist)
                        wait(20)
                    while hub.imu.heading() > -44:
                        motor_esq.run(50)
                        motor_dir.run(250)
                    andar.straight(100)
                    hub.light.on(Color.WHITE)
                    wait(1500)
                    hub.light.on(Color.RED)
                    mensagem = hub.ble.observe(2)
                    print(mensagem)
                    if mensagem == 0:
                        wait(20)
                    elif mensagem == 1:
                        hub.imu.reset_heading(0)
                        while hub.imu.heading() < 69:
                            motor_esq.run(150)
                            motor_dir.run(-50)
                            wait(20)
                        wait(500)
                        mensagem = hub.ble.observe(2)
                        while mensagem != Color.GREEN and mensagem != Color.RED:
                            mensagem = hub.ble.observe(2)
                            motor_esq.run(75)
                            motor_dir.run(75)
                            print(mensagem)
                            wait(20)
                        hub.imu.reset_heading(0)
                        andar.straight(-50)
                        while hub.imu.heading() > -134:
                            motor_esq.run(-100)
                            motor_dir.run(100)
                            wait(20)
                vez = vez + 1
                wait(20)
        wait(20)
    else:
        if dist < 90 and cooldown_obst <= 0:
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
            cooldown_obst = 3000
            estado = "linha"
        elif (esq_e_verde and dir_e_verde) or (esq == Color.GREEN and dir == Color.GREEN):
            andar.turn(-200)
            andar.straight(50)
            integral = 0
            erro_anterior = 0
            estado = "linha"
        elif esq_e_verde or esq == Color.GREEN:
            if not dirpreto and not esqpreto:
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
            else:
                andar.straight(50)
                dirpreto = False
                esqpreto = False
            integral = 0
            erro_anterior = 0
            estado = "linha"
        elif dir_e_verde or dir == Color.GREEN:
            if not dirpreto and not esqpreto:
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
            else:
                andar.straight(50)
                dirpreto = False
                esqpreto = False
            integral = 0
            erro_anterior = 0
            estado = "linha"
        elif estado == "gap":
            if na_linha():
                estado = "linha"
                integral = 0
                erro_anterior = 0
            else:
                direcao_busca = 1 if ultimo_erro >= 0 else -1
                busca.reset()
                encontrado = False
                while not na_linha() and busca.time() < 1200:
                    if direcao_busca > 0:
                        motor_esq.run(80)
                        motor_dir.run(-80)
                    else:
                        motor_esq.run(-80)
                        motor_dir.run(80)
                    wait(20)
                if na_linha():
                    encontrado = True
                if not encontrado:
                    direcao_busca = -direcao_busca
                    busca.reset()
                    while not na_linha() and busca.time() < 1200:
                        if direcao_busca > 0:
                            motor_esq.run(80)
                            motor_dir.run(-80)
                        else:
                            motor_esq.run(-80)
                            motor_dir.run(80)
                        wait(20)
                if na_linha():
                    estado = "linha"
                else:
<<<<<<< HEAD
                    if not esq_preto and meio > 80 and not dir_preto:
                        if gap == False: andar.straight(-20)
                        gap = True
                        esq_preto = e_preto(coresq)
                        dir_preto = e_preto(cordir)
                        meio = cormeio.reflection()
                        if esq_preto:
                            while meio > 20:
                                motor_esq.run(-100)
                                motor_dir.run(100)
                                meio = cormeio.reflection()
                                dir_preto = e_preto(cordir)
                                if dir_preto:
                                    while meio > 20:
                                        motor_esq.run(100)
                                        motor_dir.run(-125)
                                        meio = cormeio.reflection()
                                        dir = cordir.color()
                                    wait(20)
                                wait(20)
                            gap = False
                        elif dir_preto:
                            while meio > 25:
                                motor_esq.run(100)
                                motor_dir.run(-100)
                                meio = cormeio.reflection()
                                esq_preto = e_preto(coresq)
                                if esq_preto:
                                    while meio > 25:
                                        motor_esq.run(-125)
                                        motor_dir.run(100)
                                        meio = cormeio.reflection()
                                        esq = coresq.color()
                                        wait(20)
                                wait(20)
                            gap = False
                        else:
                            while not esq_preto and meio > 80 and not dir_preto:
                                motor_esq.run(vel)
                                motor_dir.run(vel)
                                esq_preto = e_preto(coresq)
                                dir_preto = e_preto(cordir)
                                meio = cormeio.reflection()
                                wait(200)
                    elif esq_preto and dir_preto:
                        motor_esq.run(vel)
                        motor_dir.run(vel)
                        wait(500)
                    else:
                        erro = reflection - meio
                        integral = integral + erro
                        derivada = erro - erro_anterior
                        correcao = (kp * erro) + (ki * integral) + (kd * derivada)
                        if dir_preto:
                            while meio > 25:
                                motor_esq.run(150)
                                motor_dir.run(-100)
                                meio = cormeio.reflection()
                                esq_preto = e_preto(coresq)
                                if esq_preto:
                                    while meio > 25:
                                        motor_esq.run(-125)
                                        motor_dir.run(100)
                                        meio = cormeio.reflection()
                                        esq = coresq.color()
                                        wait(20)
                                wait(20)
                            dir_preto = e_preto(cordir)
                            wait(20)
                            if meio < 20 and dir_preto:
                                omnitrix.reset()
                                while meio < 20 and tempo < 500:
                                    motor_esq.run(100)
                                    motor_dir.run(100)
                                    meio = cormeio.reflection()
                                    tempo = omnitrix.time()
                                    wait(20)
                                wait(100)
                                esq_preto = e_preto(coresq)
                                hub.imu.reset_heading(0)
                                while meio > 20 and not esq_preto and hub.imu.heading() < 100:
                                    motor_esq.run(100)
                                    motor_dir.run(-150)
                                    meio = cormeio.reflection()
                                    esq = coresq.color
                                    wait(20)
                                wait(20)
                        elif esq_preto:
                            while meio > 20:
                                motor_esq.run(-100)
                                motor_dir.run(150)
                                meio = cormeio.reflection()
                                dir_preto = e_preto(cordir)
                                if dir_preto:
                                    while meio > 20:
                                        motor_esq.run(100)
                                        motor_dir.run(-125)
                                        meio = cormeio.reflection()
                                        dir = cordir.color()
                                    wait(20)
                                wait(20)
                            esq_preto = e_preto(coresq)
                            wait(20)
                            if meio < 20 and esq_preto:
                                omnitrix.reset()
                                while meio < 20 and tempo < 500:
                                    motor_esq.run(100)
                                    motor_dir.run(100)
                                    meio = cormeio.reflection()
                                    tempo = omnitrix.time()
                                    wait(20)
                                wait(100)
                                dir_preto = e_preto(cordir)
                                hub.imu.reset_heading(0)
                                while meio > 20 and not dir_preto and hub.imu.heading() > -100:
                                    motor_esq.run(-150)
                                    motor_dir.run(100)
                                    meio = cormeio.reflection()
                                    dir = cordir.color()
                                    wait(20)
                                wait(20)
                        motor_esq.run(vel + correcao)
                        motor_dir.run(vel - correcao)
                        erro_anterior = erro
    print("esquerda: {}, meio: {}, direita: {}, distância: {}, arfagem: {}".format(esq, meio, dir, dist, arfagem))
=======
                    motor_esq.run(100)
                    motor_dir.run(100)
                    wait(500)
                    estado = "linha"
                integral = 0
                erro_anterior = 0
        elif estado == "linha":
            if dir == Color.BLACK and esq == Color.BLACK:
                motor_esq.run(vel_base)
                motor_dir.run(vel_base)
                dirpreto = True
                esqpreto = True
                wait(400)
            elif esq != Color.BLACK and meio > 50 and dir != Color.BLACK:
                motor_esq.run(vel_base)
                motor_dir.run(vel_base)
                wait(150)
                esq = coresq.color()
                dir = cordir.color()
                meio = cormeio.reflection()
                if esq != Color.BLACK and meio > 50 and dir != Color.BLACK:
                    estado = "gap"
            else:
                erro = reflection - meio
                integral = integral + erro
                if integral > 80: integral = 80
                if integral < -80: integral = -80
                derivada = erro - erro_anterior
                correcao = (kp * erro) + (ki * integral) + (kd * derivada)
                if correcao > 250: correcao = 250
                elif correcao < -250: correcao = -250
                fator_vel = abs(correcao) * 0.5
                if fator_vel > 80: fator_vel = 80
                vel_atual = vel_base - fator_vel
                if vel_atual < vel_min: vel_atual = vel_min
                ultimo_erro = erro
                if dir == Color.BLACK and not dir_e_verde:
                    dirpreto = True
                    while meio > 25 and cordir.color() == Color.BLACK:
                        motor_esq.run(80)
                        motor_dir.run(-100)
                        meio = cormeio.reflection()
                        if coresq.color() == Color.BLACK:
                            motor_esq.run(80)
                            motor_dir.run(80)
                            wait(200)
                            break
                        wait(20)
                    esq = coresq.color()
                    dir = cordir.color()
                    meio = cormeio.reflection()
                    if meio < 25:
                        motor_esq.run(vel_base)
                        motor_dir.run(vel_base)
                        wait(100)
                elif esq == Color.BLACK and not esq_e_verde:
                    esqpreto = True
                    while meio > 25 and coresq.color() == Color.BLACK:
                        motor_esq.run(-100)
                        motor_dir.run(80)
                        meio = cormeio.reflection()
                        if cordir.color() == Color.BLACK:
                            motor_esq.run(80)
                            motor_dir.run(80)
                            wait(200)
                            break
                        wait(20)
                    esq = coresq.color()
                    dir = cordir.color()
                    meio = cormeio.reflection()
                    if meio < 25:
                        motor_esq.run(vel_base)
                        motor_dir.run(vel_base)
                        wait(100)

                motor_esq.run(vel_atual + correcao)
                motor_dir.run(vel_atual - correcao)
                erro_anterior = erro
                dirpreto = False
                esqpreto = False
        else:
            estado = "linha"
    print("est: {}, esq: {}, meio: {}, dir: {}, dist: {}, arf: {}".format(estado, esq, meio, dir, dist, arfagem))
>>>>>>> 674e73e1a7324129a7c27e4c724eb1a521aebcf8
    wait(20)