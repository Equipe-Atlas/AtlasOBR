from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

# === HUB ===
hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.MAGENTA)

# === MOTORES E SENSORES ===
sensor_garra = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)
garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

garra.reset_angle(0)
selecao.reset_angle(0)
descarte.reset_angle(0)

# === PARAMETROS ===
dsaida = 110
PASSO = 200
TEMPO_PASSO = 2500
TEMPO_GIRO = 1200
LIMIAR_ENTRADA = 200
CONTADOR_MIN_ENTRADA = 3

GARRA_CIMA = 90
GARRA_BAIXO = 0
SELECAO_NEUTRO = 0
SELECAO_VIVAS = 180
DESCARTE_FECHADO = 0
DESCARTE_ABERTO = 90

# === PROTOCOLO BLE ===
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
ESTADO_VARREDURA = 1
ESTADO_CANTO = 2
ESTADO_SAIDA = 3

omnitrix = StopWatch()
estado = ESTADO_AGUARDANDO
contador_entrada = 0

# === FUNCOES ===

def le_dados_prometeu():
    dados = hub.ble.observe(1)
    if dados is None:
        return 0, 0
    if isinstance(dados, tuple) and len(dados) == 2:
        return dados[0], dados[1]
    return dados, 0

def le_distancia_frente():
    d, _ = le_dados_prometeu()
    return d

def verificou_entrada_area():
    _, flag = le_dados_prometeu()
    if flag == 1:
        return True
    if ultra_esq.distance() > LIMIAR_ENTRADA and ultra_dir.distance() > LIMIAR_ENTRADA:
        return True
    return False

def em_canto():
    return (ultra_esq.distance() < dsaida) and (ultra_dir.distance() < dsaida)

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
    # 1. Garra esta embaixo, sensor ja leu
    # 2. Seta selecao pro lado das vivas
    selecao.run_target(150, SELECAO_VIVAS)
    wait(200)
    # 3. Levanta garra (pega vitima)
    garra.run_target(200, GARRA_CIMA)
    wait(300)
    # 4. Abre descarte
    descarte.run_target(200, DESCARTE_ABERTO)
    wait(300)
    # 5. Desce garra (solta vitima)
    garra.run_target(200, GARRA_BAIXO)
    wait(300)
    # 6. Fecha descarte
    descarte.run_target(200, DESCARTE_FECHADO)
    wait(200)
    # 7. Reseta selecao
    selecao.run_target(150, SELECAO_NEUTRO)

def descarta_vitima_morta():
    # 1. Abre descarte
    descarte.run_target(200, DESCARTE_ABERTO)
    wait(300)
    # 2. Fecha descarte
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

# === LOOP PRINCIPAL ===
while True:

    if estado == ESTADO_AGUARDANDO:
        if verificou_entrada_area():
            contador_entrada += 1
        else:
            contador_entrada = 0

        if contador_entrada >= CONTADOR_MIN_ENTRADA:
            estado = ESTADO_VARREDURA
            hub.light.on(Color.GREEN)
            wait(500)

    elif estado == ESTADO_VARREDURA:
        mandar_andar()

        if tem_vitima(sensor_garra):
            pausar_prometeu()
            wait(300)

            if vitima_viva(sensor_garra):
                coleta_vitima_viva()
            elif vitima_morta(sensor_garra):
                descarta_vitima_morta()

            liberar_prometeu()
            wait(100)

        if em_canto():
            estado = ESTADO_CANTO

    elif estado == ESTADO_CANTO:
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
            estado = ESTADO_VARREDURA

    elif estado == ESTADO_SAIDA:
        hub.light.on(Color.MAGENTA)
        wait(5000)
        estado = ESTADO_AGUARDANDO
        contador_entrada = 0

    wait(20)