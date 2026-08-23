from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.BLUE)

sensor_garra = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)
garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

garra.reset_angle(0)
selecao.reset_angle(0)
descarte.reset_angle(0)

GARRA_CIMA = 90
GARRA_BAIXO = 0
SELECAO_NEUTRO = 0
SELECAO_VIVAS = 180
SELECAO_MORTAS = -180
DESCARTE_FECHADO = 0
DESCARTE_ABERTO = 90

<<<<<<< HEAD
dsaida = 100
PASSO_QUADRADO = 200
=======
dsaida = 110
PASSO = 200
>>>>>>> 916535a40ae9a3f34b6dbb7436eddd84def90d34
TEMPO_PASSO = 2500
TEMPO_GIRO = 1200

COD_ENTROU_CANTO = 100
COD_SAIDA_ESQ = 201
COD_SAIDA_FRENTE = 202
COD_SAIDA_DIR = 203
COD_PRECISA_GIRAR = 209
COD_LIBERA = 10000
COD_ANDA_FRENTE = 300
COD_GIRA_90 = 301
COD_PAUSA = 500
COD_ENTROU_AREA = 600

<<<<<<< HEAD
def em_canto():
    if (ultra_esq.distance() + ultra_dir.distance()) < dsaida:
        return True
    return False
=======
ESTADO_AGUARDANDO = 0
ESTADO_VARREDURA = 1
ESTADO_CANTO = 2
ESTADO_SAIDA = 3

omnitrix = StopWatch()
estado = ESTADO_AGUARDANDO
>>>>>>> 916535a40ae9a3f34b6dbb7436eddd84def90d34

def le_distancia_frente():
    d = hub.ble.observe(1)
    if d is None:
        return 0
    return d

def em_canto():
    return (ultra_esq.distance() < dsaida and
            ultra_dir.distance() < dsaida)

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

while True:
    mensagem = hub.ble.observe(1)

    if estado == ESTADO_AGUARDANDO:
        if mensagem == COD_ENTROU_AREA:
            hub.light.on(Color.MAGENTA)
            wait(1000)
            hub.light.on(Color.RED)
            estado = ESTADO_VARREDURA

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
<<<<<<< HEAD
            wait(200)
            hub.ble.broadcast(COD_LIBERA)
            return
        hub.ble.broadcast(COD_LIBERA)
        wait(100)
        hub.ble.broadcast(COD_GIRA_90)
        wait(TEMPO_GIRO)
while True:
    dist_esq = ultra_esq.distance()
    dist_dir = ultra_dir.distance()
    if em_canto:
        hub.ble.broadcast(200)
    wait(20)
 
=======
            wait(300)
            liberar_prometeu()
            estado = ESTADO_SAIDA
        else:
            liberar_prometeu()
            wait(100)
            mandar_girar()
            estado = ESTADO_VARREDURA

    elif estado == ESTADO_SAIDA:
        hub.light.on(Color.BLUE)
        wait(5000)
        estado = ESTADO_AGUARDANDO
    wait(20)
>>>>>>> 916535a40ae9a3f34b6dbb7436eddd84def90d34
