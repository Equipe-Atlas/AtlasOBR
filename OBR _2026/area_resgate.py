from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.GREEN)

cores = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)
garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

omnitrix = StopWatch()

dsaida = 110
COD_ENTROU_CANTO = 100   # avisa o hub do seguidor de linha pra parar e esperar
COD_SAIDA_ESQ = 201      # abertura encontrada à esquerda
COD_SAIDA_FRENTE = 202   # abertura encontrada na frente
COD_SAIDA_DIR = 203      # abertura encontrada à direita
COD_PRECISA_GIRAR = 209  # nenhuma abertura nas 3 leituras entao gira um pouco
COD_LIBERA = 10000       # devolve o controle pro seguidor de linha


def em_canto():
    return (ultra_esq.distance() + ultra_dir.distance()) < dsaida
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

Color.SILVER = Color(h=0, s=0, v=75)


def vitima_viva(sensor):
    dados = sensor.hsv()
    return dados.s < 15 and dados.v > 60


def vitima_morta(sensor):
    dados = sensor.hsv()
    return dados.v < 15


def coleta_vitima():
    garra.run_angle(200, 90)
    selecao.run_angle(150, 180)
    wait(200)
    garra.run_angle(200, -90)


def descarta_vitima():
    descarte.run_angle(200, 90)
    wait(200)
    descarte.run_angle(200, -90)


def varredura_normal():
    if vitima_viva(cores):
        coleta_vitima()
    elif vitima_morta(cores):
        descarta_vitima()

while True:
    if em_canto():
        hub.ble.broadcast(COD_ENTROU_CANTO)
        wait(50)

        resultado = verifica_saida()

        if resultado == COD_PRECISA_GIRAR:
            hub.ble.broadcast(COD_PRECISA_GIRAR)
        else:
            hub.ble.broadcast(resultado)
            wait(200)
            hub.ble.broadcast(COD_LIBERA)
    else:
        varredura_normal()

    wait(20)