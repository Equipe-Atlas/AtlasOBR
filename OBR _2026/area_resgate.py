from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

# === HUB ===
hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.BLUE)

# === SENSORES E MOTORES ===
sensor_garra = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)
garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

garra.reset_angle(0)
selecao.reset_angle(0)
descarte.reset_angle(0)

# === POSICOES DOS MOTORES ===
GARRA_CIMA = 90
GARRA_BAIXO = 0
SELECAO_NEUTRO = 0
SELECAO_VIVAS = 180
SELECAO_MORTAS = -180
DESCARTE_FECHADO = 0
DESCARTE_ABERTO = 90

# === PARAMETROS ===
dsaida = 100
PASSO_QUADRADO = 200
TEMPO_PASSO = 2500
TEMPO_GIRO = 1200
LIMIAR_VITIMA = 60
TEMPO_MAX_VARREDURA_ANGULAR = 8000

# === CODIGOS BLE ===
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

# === ESTADOS ===
ESTADO_AGUARDANDO = 0
ESTADO_VARREDURA_EXTERNA = 1
ESTADO_VARREDURA_INTERNA = 2
ESTADO_COLETA_VITIMA = 3
ESTADO_ENTREGA_VITIMA = 4
ESTADO_PROCURA_SAIDA = 5
ESTADO_SAIDA = 6

omnitrix = StopWatch()
estado = ESTADO_AGUARDANDO

# === MAPEAMENTO DA SALA (logica do repositorio) ===
quina_atual = 0
# 0 = vazio, 2 = saida, 3 = resgate vivo, 4 = resgate morto
tras_direita = 0
frente_direita = 0
frente_esquerda = 0
tras_esquerda = 0

# Angulos das areas de resgate (setados durante varredura)
angulo_resgate_vivo = 0
angulo_resgate_morto = 0
angulo_saida = 0
angulo_offset = 0

# Controle de varredura angular
timer_varredura_angular = 0
tem_vitima = False

# === FUNCOES ===

def em_canto():
    if (ultra_esq.distance() + ultra_dir.distance()) < dsaida:
        return True
    return False

def le_distancia_frente():
    d = hub.ble.observe(1)
    if d is None:
        return 0
    return d

def verifica_saida():
    d_esq = ultra_esq.distance()
    d_frente = le_distancia_frente()
    d_dir = ultra_dir.distance()
    if d_esq > dsaida:
        return COD_SAIDA_ESQ
    if d_frente > dsaida:
        return COD_SAIDA_FRENTE
    if d_dir > dsaida:
        return COD_SAIDA_DIR
    return COD_PRECISA_GIRAR

def vitima_viva(sensor):
    dados = sensor.hsv()
    return dados.s < 15 and dados.v > 60

def vitima_morta(sensor):
    dados = sensor.hsv()
    return dados.v < 15

def tem_vitima(sensor):
    return vitima_viva(sensor) or vitima_morta(sensor)

def coleta_vitima_viva():
    selecao.run_target(150, SELECAO_VIVAS)
    wait(200)
    garra.run_target(200, GARRA_CIMA)
    wait(300)
    descarte.run_target(200, DESCARTE_ABERTO)
    wait(300)
    garra.run_target(200, GARRA_BAIXO)
    wait(300)
    descarte.run_target(200, DESCARTE_FECHADO)
    wait(200)
    selecao.run_target(150, SELECAO_NEUTRO)

def descarta_vitima_morta():
    descarte.run_target(200, DESCARTE_ABERTO)
    wait(300)
    descarte.run_target(200, DESCARTE_FECHADO)
    wait(200)

def mandar_andar():
    hub.ble.broadcast(COD_ANDA_FRENTE)
    wait(TEMPO_PASSO)

def mandar_girar():
    hub.ble.broadcast(COD_GIRA_90)
    wait(TEMPO_GIRO)

def pausar_prometeu():
    hub.ble.broadcast(COD_PAUSA)
    wait(100)

def liberar_prometeu():
    hub.ble.broadcast(COD_LIBERA)
    wait(100)

def ler_angulo_virtual():
    """Le o angulo virtual baseado no heading do IMU, igual ao repositorio."""
    heading = hub.imu.heading()
    if heading > angulo_offset:
        return heading - angulo_offset
    elif heading < angulo_offset:
        return (360 + heading) - angulo_offset
    else:
        return 0

# === LOOP PRINCIPAL ===
while True:
    dist_esq = ultra_esq.distance()
    dist_dir = ultra_dir.distance()
    if estado == ESTADO_AGUARDANDO:
        # Deteccao de entrada na area de resgate usando em_canto()
        if em_canto():
            hub.light.on(Color.MAGENTA)
            hub.ble.broadcast(COD_ENTROU_AREA)
            wait(1000)
            hub.light.on(Color.RED)
            angulo_offset = hub.imu.heading()
            quina_atual = 0
            estado = ESTADO_VARREDURA_EXTERNA

    elif estado == ESTADO_VARREDURA_EXTERNA:
        # Anda um passo e checa vitima e cantos
        mandar_andar()

        # Checa vitima na garra
        if tem_vitima(sensor_garra):
            pausar_prometeu()
            wait(300)
            if vitima_viva(sensor_garra):
                coleta_vitima_viva()
            elif vitima_morta(sensor_garra):
                descarta_vitima_morta()
            liberar_prometeu()
            wait(100)

        # Checa se bateu num canto (parede dos dois lados)
        if em_canto():
            quina_atual += 1

            # Mapeia a quina atual baseado na leitura dos ultrassonicos
            # Se um dos lados abriu, pode ser saida ou area de resgate
            d_esq = ultra_esq.distance()
            d_dir = ultra_dir.distance()
            d_frente = le_distancia_frente()

            angulo_virtual = ler_angulo_virtual()

            # Se a frente abriu (distancia grande), pode ser saida
            if d_frente > dsaida * 3:
                # Marca como saida
                if quina_atual == 1:
                    tras_direita = 2
                    angulo_saida = 90
                elif quina_atual == 2:
                    frente_direita = 2
                    angulo_saida = 0
                elif quina_atual == 3:
                    frente_esquerda = 2
                    angulo_saida = 180
                elif quina_atual == 4:
                    tras_esquerda = 2
                    angulo_saida = 270
            else:
                # Marca como area de resgate (precisa ajustar com calibracao)
                # Por enquanto assume vivo se brilho alto, morto se baixo
                if quina_atual == 1:
                    tras_direita = 3
                    angulo_resgate_vivo = 135
                elif quina_atual == 2:
                    frente_direita = 4
                    angulo_resgate_morto = 45
                elif quina_atual == 3:
                    frente_esquerda = 3
                    angulo_resgate_vivo = 315
                elif quina_atual == 4:
                    tras_esquerda = 4
                    angulo_resgate_morto = 225

            # Se completou as 4 quinas, vai pra varredura interna
            if quina_atual >= 4:
                # Manda o Prometeu ir pro centro da sala
                for _ in range(3):
                    mandar_andar()
                angulo_offset = hub.imu.heading()
                omnitrix.reset()
                estado = ESTADO_VARREDURA_INTERNA
            else:
                # Gira 90 graus e continua a varredura externa
                mandar_girar()
                angulo_offset = hub.imu.heading()

    elif estado == ESTADO_VARREDURA_INTERNA:
        # Varredura angular: gira em incrementos procurando vitimas
        timer_varredura_angular = omnitrix.time()

        if timer_varredura_angular > TEMPO_MAX_VARREDURA_ANGULAR:
            # Tempo esgotado, vai procurar a saida
            estado = ESTADO_PROCURA_SAIDA
        else:
            # Gira 90 graus e checa vitima
            mandar_girar()
            angulo_virtual = ler_angulo_virtual()

            # Checa vitima na garra apos o giro
            if tem_vitima(sensor_garra):
                pausar_prometeu()
                wait(300)

                angulo_vitima = angulo_virtual

                if vitima_viva(sensor_garra):
                    coleta_vitima_viva()

                    # Navega ate a area de resgate vivo
                    # Gira ate alcancar o angulo da area vivo
                    while True:
                        angulo_virtual = ler_angulo_virtual()
                        if (angulo_virtual > (angulo_resgate_vivo - 10) and
                            angulo_virtual < (angulo_resgate_vivo + 10)):
                            break
                        hub.ble.broadcast(COD_GIRA_90)
                        wait(TEMPO_GIRO)

                    # Entrega a vitima
                    descarte.run_target(200, DESCARTE_ABERTO)
                    wait(300)
                    descarte.run_target(200, DESCARTE_FECHADO)
                    wait(200)

                elif vitima_morta(sensor_garra):
                    descarta_vitima_morta()

                    # Navega ate a area de resgate morto
                    while True:
                        angulo_virtual = ler_angulo_virtual()
                        if (angulo_virtual > (angulo_resgate_morto - 10) and
                            angulo_virtual < (angulo_resgate_morto + 10)):
                            break
                        hub.ble.broadcast(COD_GIRA_90)
                        wait(TEMPO_GIRO)

                    # Entrega a vitima morta
                    descarte.run_target(200, DESCARTE_ABERTO)
                    wait(300)
                    descarte.run_target(200, DESCARTE_FECHADO)
                    wait(200)

                # Retorna ao centro (manda andar de volta)
                liberar_prometeu()
                wait(100)
                # Reseta o timer pra continuar procurando
                omnitrix.reset()

    elif estado == ESTADO_COLETA_VITIMA:
        # Estado reservado caso precise separar a coleta
        pausar_prometeu()
        wait(300)

        if vitima_viva(sensor_garra):
            coleta_vitima_viva()
        elif vitima_morta(sensor_garra):
            descarta_vitima_morta()

        liberar_prometeu()
        wait(100)
        estado = ESTADO_VARREDURA_INTERNA

    elif estado == ESTADO_ENTREGA_VITIMA:
        # Navega ate a area de resgate correta
        angulo_virtual = ler_angulo_virtual()
        angulo_alvo = angulo_resgate_vivo  # ou morto, dependendo

        while True:
            angulo_virtual = ler_angulo_virtual()
            if (angulo_virtual > (angulo_alvo - 10) and
                angulo_virtual < (angulo_alvo + 10)):
                break
            mandar_girar()

        # Entrega
        descarte.run_target(200, DESCARTE_ABERTO)
        wait(300)
        descarte.run_target(200, DESCARTE_FECHADO)
        wait(200)

        estado = ESTADO_VARREDURA_INTERNA

    elif estado == ESTADO_PROCURA_SAIDA:
        # Manda o Prometeu ate bater num canto
        mandar_andar()

        if em_canto():
            hub.ble.broadcast(COD_ENTROU_CANTO)
            wait(200)

            resultado = verifica_saida()

            if resultado in (COD_SAIDA_ESQ, COD_SAIDA_FRENTE, COD_SAIDA_DIR):
                hub.ble.broadcast(resultado)
                wait(300)
                liberar_prometeu()
                estado = ESTADO_SAIDA
            else:
                liberar_prometeu()
                wait(100)
                mandar_girar()
                # Continua procurando

    elif estado == ESTADO_SAIDA:
        hub.light.on(Color.BLUE)
        wait(5000)
        estado = ESTADO_AGUARDANDO
        quina_atual = 0
        tras_direita = 0
        frente_direita = 0
        frente_esquerda = 0
        tras_esquerda = 0
        angulo_resgate_vivo = 0
        angulo_resgate_morto = 0
        angulo_saida = 0
    print(dist_esq, dist_dir)
    wait(20)