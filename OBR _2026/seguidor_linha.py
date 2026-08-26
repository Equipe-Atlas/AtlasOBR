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
reflection = 36
vel = 150
kp = 6
ki = 0.01
kd = 20
integral = 0
erro_anterior = 0
ultimo_dist = 0
tempo = 0
gap = False

def mapeia_verde(sensor):
    dados = sensor.hsv()
    if (160 <= dados.h <= 200) and (dados.s > 40) and (40 <= dados.v <= 100):
        return True
    return False

def e_preto(sensor):
    dados = sensor.hsv()
    if (dados.h > 170) and (dados.s < 50) and (dados.v < 80):
        return True
    return False

hub.imu.reset_heading(0)
hub.light.on(Color.BLUE)

while True:
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    esq_preto = e_preto(coresq)
    dir_preto = e_preto(cordir)
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

    if arfagem > 3 or arfagem < -2:
        passou_rampa = True
        if arfagem > 3:
            vel = 300
        elif arfagem < -3:
            vel = 150
        hub.imu.reset_heading(0)
        while arfagem > 3:
            guinada = hub.imu.heading()
            arfagem, rolagem = hub.imu.tilt()
            arfagem = arfagem + 3.6
            dir_preto = e_preto(cordir)
            esq_preto = e_preto(coresq)
            ad = 0
            ae = 0
            if dir_preto:
                ae = 200
            elif esq == Color.BLACK:
                ad = 200
            motor_esq.run(guinada * -10 + vel + ae)
            motor_dir.run(guinada * 10 + vel + ad)
            wait(20)
            while arfagem < -2 and arfagem > -11:
                motor_esq.run(150)
                motor_dir.run(150)
                arfagem, rolagem = hub.imu.tilt()
                arfagem = arfagem + 3.6
                wait(20)
    else:
        if mensagem == 200:
            andar.stop()
            wait(500)
            # --- FASE 1: Medir eixo X (parede frontal) ---
            dist_frente = 0
            for _ in range(3):
                dist_frente += ultra.distance()
                wait(10)
            dist_frente = dist_frente // 3
            print("Dist frente (X):", dist_frente)
            offset_sensor = 50
            distancia_x = (dist_frente / 2) - offset_sensor
            if distancia_x > 0:
                andar.straight(distancia_x)
            andar.stop()
            wait(500)
            # --- FASE 2: Girar 90 graus a direita ---
            hub.imu.reset_heading(0)
            while hub.imu.heading() < 85:
                motor_esq.run(100)
                motor_dir.run(-100)
                wait(20)
            motor_esq.stop()
            motor_dir.stop()
            wait(500)
            # --- FASE 3: Medir eixo Y (parede lateral, agora frontal) ---
            dist_lateral = 0
            for _ in range(3):
                dist_lateral += ultra.distance()
                wait(10)
            dist_lateral = dist_lateral // 3
            print("Dist lateral (Y):", dist_lateral)
            distancia_y = (dist_lateral / 2) - offset_sensor
            if distancia_y > 0:
                andar.straight(distancia_y)
            andar.stop()
            wait(500)
            # --- FASE 4: Girar -90 graus (voltar a orientacao original) ---
            hub.imu.reset_heading(0)
            while hub.imu.heading() > -85:
                motor_esq.run(-100)
                motor_dir.run(100)
                wait(20)
            motor_esq.stop()
            motor_dir.stop()
            wait(500)
            # --- FASE 5: Avisar Atlas que centralizou ---
            hub.ble.broadcast(400)
            wait(500)
            # --- FASE 6: Seguir comandos do Atlas na busca de vitimas ---
            while True:
                msg = hub.ble.observe(2)
                if msg is None:
                    msg = 0
                if msg == 301:      # Parar (Atlas achou vitima)
                    motor_esq.stop()
                    motor_dir.stop()
                elif msg == 302:    # Ir pra frente
                    motor_esq.run(80)
                    motor_dir.run(80)
                elif msg == 303:    # Girar pra direita
                    motor_esq.run(80)
                    motor_dir.run(-80)
                elif msg == 304:    # Girar pra esquerda
                    motor_esq.run(-80)
                    motor_dir.run(80)
                elif msg == 305:    # Continuar buscando
                    motor_esq.run(80)
                    motor_dir.run(80)
                elif msg == 600:    # Fim, todas coletadas
                    motor_esq.stop()
                    motor_dir.stop()
                    break
                wait(20)
            # Depois do resgate, volta pro seguidor de linha
            integral = 0
            erro_anterior = 0
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
                andar.turn(90)
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
                if esq_e_verde and dir_e_verde:
                    andar.turn(-200)
                    andar.straight(50)
                elif esq_e_verde:
                    while esq != Color.WHITE:
                        motor_esq.run(-50)
                        motor_dir.run(-75)
                        esq = coresq.color()
                    andar.straight(20)
                    dir_e_verde = mapeia_verde(cordir)
                    wait(100)
                    if dir_e_verde:
                        andar.turn(-200)
                        andar.straight(50)
                    else:
                        andar.straight(40)
                        andar.turn(-90)
                        andar.straight(40)
                elif dir_e_verde:
                    while dir != Color.WHITE:
                        motor_esq.run(-75)
                        motor_dir.run(-50)
                        dir = cordir.color()
                    andar.straight(20)
                    esq_e_verde = mapeia_verde(coresq)
                    wait(100)
                    if  esq_e_verde:
                        andar.turn(-200)
                        andar.straight(50)
                    else:
                        andar.straight(40)
                        andar.turn(90)
                        andar.straight(40)
                else:
                    if not esq_preto and meio > 80 and not dir_preto:
                        if gap == False: andar.straight(-20)
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
                                if esq_preto:
                                    while meio > 25:
                                        motor_esq.run(-125)
                                        motor_dir.run(100)
                                        meio = cormeio.reflection()
                                        wait(20)
                                wait(20)
                            gap = False
                        else:
                            if meio > 80: gap = True
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
                            while meio > 20:
                                motor_esq.run(125)
                                motor_dir.run(-100)
                                meio = cormeio.reflection()
                                esq_preto = e_preto(coresq)
                                if esq_preto:
                                    while meio > 20:
                                        motor_esq.run(-125)
                                        motor_dir.run(100)
                                        meio = cormeio.reflection()
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
                                dir_e_verde = mapeia_verde(cordir)
                                if dir_e_verde: andar.straight(40)
                                while meio > 20 and hub.imu.heading() < 100:
                                    motor_esq.run(125)
                                    motor_dir.run(-100)
                                    meio = cormeio.reflection()
                                    esq_preto = e_preto(coresq)
                                    if esq_preto:
                                        while meio > 20:
                                            motor_esq.run(-125)
                                            motor_dir.run(100)
                                            meio = cormeio.reflection()
                                            wait(20)
                                    wait(20)
                                if hub.imu.heading() > 100 or hub.imu.heading() == 100:
                                    while meio > 20:
                                        motor_esq.run(100)
                                        motor_dir.run(-125)
                                        meio = cormeio.reflection()
                                        wait(20)
                        elif esq_preto:
                            while meio > 20:
                                motor_esq.run(-100)
                                motor_dir.run(125)
                                meio = cormeio.reflection()
                                dir_preto = e_preto(cordir)
                                if dir_preto:
                                    while meio > 20:
                                        motor_esq.run(100)
                                        motor_dir.run(-125)
                                        meio = cormeio.reflection()
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
                                esq_e_verde = mapeia_verde(coresq)
                                if esq_e_verde: andar.straight(40)
                                while meio > 20 and not dir_preto and hub.imu.heading() > -100:
                                    motor_esq.run(-100)
                                    motor_dir.run(125)
                                    meio = cormeio.reflection()
                                    dir_preto = e_preto(cordir)
                                    if dir_preto:
                                        while meio > 20:
                                            motor_esq.run(100)
                                            motor_dir.run(-125)
                                            meio = cormeio.reflection()
                                        wait(20)
                                    wait(20)
                                if hub.imu.heading() > 100 or hub.imu.heading() == 100:
                                    while meio > 20:
                                        motor_esq.run(100)
                                        motor_dir.run(-125)
                                        meio = cormeio.reflection()
                                        wait(20)
                        motor_esq.run(vel + correcao)
                        motor_dir.run(vel - correcao)
                        erro_anterior = erro
    print("esquerda: {}, meio: {}, direita: {}, distância: {}, arfagem: {}".format(esq, meio, dir, dist, arfagem))
    wait(20)