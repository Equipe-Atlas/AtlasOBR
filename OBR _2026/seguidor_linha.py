from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

# === HUB ===
hub = PrimeHub(broadcast_channel=1, observe_channels=[2])
hub.light.on(Color.BLUE)

# === MOTORES E SENSORES ===
ultra = UltrasonicSensor(Port.C)
cordir = ColorSensor(Port.B)
cormeio = ColorSensor(Port.A)
coresq = ColorSensor(Port.D)
motor_esq = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E)
andar = DriveBase(motor_esq, motor_dir, 63, 133)
andar.settings(straight_speed=100, straight_acceleration=300,
               turn_rate=100, turn_acceleration=300)

# === CORES ===
Color.BLACK = Color(h=240, s=100, v=20)
Color.WHITE = Color(h=0, s=0, v=100)
cores_detectaveis = (Color.GREEN, Color.BLACK,
                     Color.WHITE, Color.NONE, Color.RED)
cordir.detectable_colors(cores_detectaveis)
coresq.detectable_colors(cores_detectaveis)

# === PROTOCOLO BLE ===
COD_ENTROU_CANTO = 100
COD_SAIDA_ESQ = 201
COD_SAIDA_FRENTE = 202
COD_SAIDA_DIR = 203
COD_PRECISA_GIRAR = 209
COD_LIBERA = 10000
COD_ANDA_FRENTE = 300
COD_GIRA_90 = 301
PASSO_QUADRADO = 200

# === PID ===
reflection = 36
vel = 150
kp = 4
ki = 0.05
kd = 20
integral = 0
erro_anterior = 0
ultimo_dist = 0

# === ESTADO ===
omnitrix = StopWatch()
dirpreto = False
esqpreto = False
tempo = 0
na_area_resgate = False
ultimo_comando_resgate = None
contador_resgate = 0

# === PARAMETROS DE DETECCAO ===
LIMIAR_ENTRADA = 200       # dist > isso = espaco aberto (entrou na area)
CONTADOR_MIN_ENTRADA = 3   # quantas leituras seguidas pra confirmar entrada

# === FUNCOES AUXILIARES ===

def mapeia_verde(sensor):
    dados = sensor.hsv()
    return (160 <= dados.h <= 200) and (dados.s > 40) and (50 <= dados.v <= 100)

def detectou_entrada_resgate(distancia):
    """Detecta entrada na area de resgate usando o ultrassonico da frente.
    Se a distancia for maior que o limiar, significa espaco aberto a frente."""
    return distancia > LIMIAR_ENTRADA

def encontra_linha():
    """Gira ate reencontrar a linha preta no sensor do meio."""
    meio = cormeio.reflection()
    omnitrix.reset()
    while meio > 25 and omnitrix.time() < 1500:
        motor_esq.run(100)
        motor_dir.run(-100)
        meio = cormeio.reflection()
        wait(20)
    if meio > 25:
        omnitrix.reset()
        while meio > 25 and omnitrix.time() < 3000:
            motor_esq.run(-100)
            motor_dir.run(100)
            meio = cormeio.reflection()
            wait(20)
    motor_esq.stop()
    motor_dir.stop()
    integral = 0
    erro_anterior = 0

# === INICIALIZACAO ===
hub.imu.reset_heading(0)

# === LOOP PRINCIPAL ===
while True:
    # --- LEITURAS ---
    esq_e_verde = mapeia_verde(coresq)
    dir_e_verde = mapeia_verde(cordir)
    dist = ultra.distance()
    esq = coresq.color()
    dir = cordir.color()
    meio = cormeio.reflection()
    arfagem, rolagem = hub.imu.tilt()
    arfagem = arfagem + 3.6
    mensagem = hub.ble.observe(2)
    vel = 150

    # --- BROADCAST: manda (distancia, flag_resgate) pro Atlas ---
    flag_resgate = 1 if na_area_resgate else 0
    hub.ble.broadcast((dist, flag_resgate))

    # --- DETECCAO DE ENTRADA NA AREA DE RESGATE (ultrassonico) ---
    if not na_area_resgate:
        if detectou_entrada_resgate(dist):
            contador_resgate += 1
        else:
            contador_resgate = 0

        if contador_resgate >= CONTADOR_MIN_ENTRADA:
            na_area_resgate = True
            hub.light.on(Color.MAGENTA)
            andar.stop()
            wait(500)

    # --- RAMPAS (arfagem) ---
    if arfagem > 5 or arfagem < -5:
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

    # --- COMANDOS DO ATLAS (CANTO / SAIDA) ---
    elif mensagem == COD_ENTROU_CANTO:
        andar.stop()
        ultima_mensagem_tratada = None
        achou_saida = False
        while True:
            mensagem = hub.ble.observe(2)
            if mensagem == COD_LIBERA:
                if achou_saida:
                    na_area_resgate = False
                    contador_resgate = 0
                    hub.light.on(Color.BLUE)
                    encontra_linha()
                break
            elif mensagem != ultima_mensagem_tratada:
                if mensagem == COD_SAIDA_ESQ:
                    andar.turn(-90)
                    achou_saida = True
                elif mensagem == COD_SAIDA_FRENTE:
                    andar.straight(100)
                    achou_saida = True
                elif mensagem == COD_SAIDA_DIR:
                    andar.turn(90)
                    achou_saida = True
                elif mensagem == COD_PRECISA_GIRAR:
                    andar.turn(30)
                ultima_mensagem_tratada = mensagem
            wait(20)

    # --- MODO AREA DE RESGATE ---
    elif na_area_resgate:
        if mensagem != ultimo_comando_resgate:
            if mensagem == COD_ANDA_FRENTE:
                andar.straight(PASSO_QUADRADO)
            elif mensagem == COD_GIRA_90:
                andar.turn(90)
            ultimo_comando_resgate = mensagem

    # --- SEGUE LINHA NORMAL ---
    else:
        # Obstaculo a frente
        if dist < 75:
            andar.turn(80)
            ultimo_dist = ultra.distance()
            while dist <= ultimo_dist:
                ultimo_dist = ultra.distance()
                motor_esq.run(-100)
                motor_dir.run(100)
                wait(20)
                dist = ultra.distance()
                if dist > 300:
                    dist = 300
                if ultimo_dist > 300:
                    ultimo_dist = 300
                if dist > (ultimo_dist + 1):
                    dist = ultimo_dist
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

        # Verde dos dois lados
        elif (esq_e_verde and dir_e_verde) or (esq == Color.GREEN and dir == Color.GREEN):
            andar.turn(-200)
            andar.straight(50)

        # Verde esquerdo
        elif esq_e_verde or esq == Color.GREEN:
            if not dirpreto and not esqpreto:
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
                    andar.straight(40)
                    andar.turn(-90)
                    andar.straight(40)
            elif esqpreto or dirpreto:
                andar.straight(50)
                dirpreto = False
                esqpreto = False

        # Verde direito
        elif dir_e_verde or dir == Color.GREEN:
            if not dirpreto and not esqpreto:
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
                    andar.straight(40)
                    andar.turn(90)
                    andar.straight(40)
                dirpreto = False
            elif esqpreto or dirpreto:
                andar.straight(50)
                dirpreto = False
                esqpreto = False

        # PID normal
        else:
            if esq == Color.WHITE and meio > 50 and dir == Color.WHITE:
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
                integral = max(-100, min(100, integral))
                derivada = erro - erro_anterior
                correcao = (kp * erro) + (ki * integral) + (kd * derivada)
                correcao = max(-300, min(300, correcao))

                if dir == Color.BLACK and not dir_e_verde:
                    dirpreto = True
                    while meio > 25:
                        motor_esq.run(100)
                        motor_dir.run(-125)
                        meio = cormeio.reflection()
                        esq = coresq.color()
                        if esq != Color.WHITE:
                            while meio > 25:
                                motor_esq.run(-100)
                                motor_dir.run(100)
                                meio = cormeio.reflection()
                                esq = coresq.color()
                                wait(20)
                        wait(20)
                    dir = cordir.color()
                    if meio < 25 and dir == Color.BLACK:
                        omnitrix.reset()
                        tempo = 0
                        while meio < 25 and tempo < 600:
                            motor_esq.run(100)
                            motor_dir.run(100)
                            meio = cormeio.reflection()
                            tempo = omnitrix.time()
                            wait(20)
                        wait(100)
                        while meio > 25:
                            motor_esq.run(100)
                            motor_dir.run(-150)
                            meio = cormeio.reflection()
                            esq = coresq.color()
                            wait(20)

                elif esq == Color.BLACK and not esq_e_verde:
                    esqpreto = True
                    while meio > 25:
                        motor_esq.run(-125)
                        motor_dir.run(100)
                        meio = cormeio.reflection()
                        dir = cordir.color()
                        if dir != Color.WHITE:
                            while meio > 25:
                                motor_esq.run(100)
                                motor_dir.run(-100)
                                meio = cormeio.reflection()
                                dir = cordir.color()
                            wait(20)
                        wait(20)
                    esq = coresq.color()
                    if meio < 25 and esq == Color.BLACK:
                        omnitrix.reset()
                        tempo = 0
                        while meio < 25 and tempo < 600:
                            motor_esq.run(100)
                            motor_dir.run(100)
                            meio = cormeio.reflection()
                            tempo = omnitrix.time()
                            wait(20)
                        wait(100)
                        while meio > 25:
                            motor_esq.run(-150)
                            motor_dir.run(100)
                            meio = cormeio.reflection()
                            dir = cordir.color()
                            wait(20)

                motor_esq.run(vel + correcao)
                motor_dir.run(vel - correcao)
                erro_anterior = erro
                dirpreto = False
                esqpreto = False

    wait(20)